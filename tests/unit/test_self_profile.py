"""Perfil propio: identidad, secretos, validación y cambios atómicos."""

import pytest

from src.infrastructure.security.passwords import Argon2PasswordHasher


@pytest.fixture
def own_profile(authenticated_accounts):
    client, repository, rows = authenticated_accounts
    repository.cuentas[0].rol = "cliente"
    return client, repository, rows


def test_edita_perfil_y_password_literal(own_profile):
    client, repository, rows = own_profile
    before = client.get("/v1/users/me").json()
    old_hash = repository.cuentas[0].password_hash
    result = client.patch("/v1/users/me", json={"nombre": "  Nueva  "})
    assert result.status_code == 200 and result.json()["nombre"] == "Nueva"
    assert repository.cuentas[0].password_hash == old_hash
    password = " nueva contraseña literal "
    result = client.patch(
        "/v1/users/me",
        json={
            "email": "NUEVA@example.com",
            "password": password,
            "current_password": "contraseña de prueba",
        },
    )
    assert result.status_code == 200 and result.json()["email"] == "nueva@example.com"
    assert "password" not in result.text
    for field in ("id", "rol", "activo", "fecha_creacion", "id_cliente"):
        assert result.json()[field] == before[field]
    assert Argon2PasswordHasher().verify(password, repository.cuentas[0].password_hash)
    assert not Argon2PasswordHasher().verify(
        password.strip(), repository.cuentas[0].password_hash
    )
    assert repository.cuentas[1].nombre == rows[1]["nombre"]


def test_rechazo_no_cambia_datos(own_profile):
    client, repository, rows = own_profile
    before = client.get("/v1/users/me").json()
    previous_hash = repository.cuentas[0].password_hash
    for current, email, expected in (
        ("clave incorrecta", "otra@example.com", 403),
        ("contraseña de prueba", rows[1]["email"], 409),
    ):
        response = client.patch(
            "/v1/users/me",
            json={
                "nombre": "No guardar",
                "email": email,
                "password": "contraseña distinta",
                "current_password": current,
            },
        )
        assert response.status_code == expected
        assert current not in response.text
        assert "www-authenticate" not in response.headers
        assert client.get("/v1/users/me").json() == before
        assert repository.cuentas[0].password_hash == previous_hash


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"nombre": None},
        {"email": None},
        {"password": None},
        {"current_password": None},
        {"current_password": "contraseña de prueba"},
        {"password": "contraseña nueva"},
        {"password": "corta", "current_password": "contraseña de prueba"},
        {"rol": "admin"},
        {"activo": False},
        {"id_cliente": 1},
        {"id": 2},
        {"email": "incorrecto"},
        {"nombre": "  "},
    ],
)
def test_valida_sin_revelar_credenciales(own_profile, payload):
    client, repository, _ = own_profile
    previous_hash = repository.cuentas[0].password_hash
    response = client.patch("/v1/users/me", json=payload)
    assert response.status_code == 422
    assert all(
        "input" not in error and "ctx" not in error
        for error in response.json()["detail"]
    )
    assert repository.cuentas[0].password_hash == previous_hash


@pytest.mark.parametrize("rol", ["cliente", "staff"])
def test_no_elude_password_actual_por_id(own_profile, rol):
    client, repository, rows = own_profile
    repository.cuentas[0].rol = rol
    for row in rows:
        for method in ("PUT", "PATCH"):
            result = client.request(
                method,
                f"/v1/users/{row['id']}",
                json={
                    "nombre": "Cambio",
                    "email": "otra@example.com",
                    "password": "contraseña nueva",
                },
            )
            assert result.status_code == 403
    assert client.get(f"/v1/users/{rows[0]['id']}").status_code == 200
    assert client.get(f"/v1/users/{rows[1]['id']}").status_code == 403
    client.headers.pop("Authorization")
    assert client.patch("/v1/users/me", json={"nombre": "Cambio"}).status_code == 401
