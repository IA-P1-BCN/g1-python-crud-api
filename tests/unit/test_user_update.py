"""Edición de Cuenta con validación, hash y campos protegidos."""

import pytest

from src.infrastructure.security.passwords import Argon2PasswordHasher


def test_put_patch_conservan_campos_y_actualizan_hash(authenticated_accounts):
    client, repository, rows = authenticated_accounts
    row = rows[1]
    url = f"/v1/users/{row['id']}"
    old_hash = repository.get(row["id"]).password_hash
    response = client.put(
        url, json={"nombre": "Cambiado", "email": "CAMBIO@example.com"}
    )
    assert (
        response.status_code == 200 and response.json()["email"] == "cambio@example.com"
    )
    assert repository.get(row["id"]).password_hash == old_hash
    password = " nueva contraseña literal "
    response = client.patch(url, json={"password": password})
    assert response.status_code == 200 and "password" not in response.text
    for key in ("id", "activo", "rol", "fecha_creacion", "id_cliente"):
        assert response.json()[key] == row[key]
    assert response.json()["nombre"] == "Cambiado"
    assert Argon2PasswordHasher().verify(
        password, repository.get(row["id"]).password_hash
    )
    assert not Argon2PasswordHasher().verify(
        "contraseña de prueba", repository.get(row["id"]).password_hash
    )


@pytest.mark.parametrize(
    "method,data",
    [
        ("put", {"nombre": "Falta email"}),
        ("patch", {}),
        ("patch", {"nombre": None}),
        ("patch", {"email": None}),
        ("patch", {"password": None}),
        ("patch", {"password": "corta"}),
        ("patch", {"nombre": " "}),
        ("patch", {"email": "incorrecto"}),
        ("patch", {"rol": "admin"}),
        ("patch", {"activo": False}),
        ("patch", {"id_cliente": 1}),
    ],
)
def test_edicion_invalida(authenticated_accounts, method, data):
    client, _, rows = authenticated_accounts
    response = getattr(client, method)(f"/v1/users/{rows[1]['id']}", json=data)
    assert response.status_code == 422
    assert "corta" not in response.text


def test_edicion_404_409_y_proteccion(authenticated_accounts):
    client, repository, rows = authenticated_accounts
    assert client.patch("/v1/users/99999", json={"nombre": "Cambio"}).status_code == 404
    previous = repository.get(rows[1]["id"]).password_hash
    result = client.patch(
        f"/v1/users/{rows[1]['id']}",
        json={"email": rows[0]["email"], "password": "otra contraseña distinta"},
    )
    assert result.status_code == 409
    assert repository.get(rows[1]["id"]).password_hash == previous
    client.headers.pop("Authorization")
    assert (
        client.put(
            "/v1/users/1", json={"nombre": "Ana", "email": "ana@example.com"}
        ).status_code
        == 401
    )
    assert client.patch("/v1/users/1", json={"nombre": "Ana"}).status_code == 401
