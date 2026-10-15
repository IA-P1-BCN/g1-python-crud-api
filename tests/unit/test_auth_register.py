"""Contrato HTTP de alta, validación y no exposición de contraseñas."""

import pytest


def test_alta_y_email_duplicado(registration_client):
    client, repository = registration_client
    payload = {
        "nombre": "Ana",
        "email": "ANA@example.com",
        "password": " contraseña intacta ",
    }
    response = client.post("/v1/auth/register", json=payload)
    assert response.status_code == 201
    assert response.json()["email"] == "ana@example.com"
    assert response.json()["rol"] == "cliente"
    assert response.json()["id_cliente"] is None
    assert "password" not in response.text
    assert repository.cuentas[0].password_hash.startswith("$argon2id$")
    assert client.post("/v1/auth/register", json=payload).status_code == 409


@pytest.mark.parametrize(
    "changes",
    [
        {"nombre": " "},
        {"email": "no-email"},
        {"password": "corta"},
        {"password": "x" * 129},
        {"rol": "admin"},
        {"activo": True},
        {"id_cliente": 1},
    ],
)
def test_validacion_no_filtra_secretos(registration_client, changes):
    client, repository = registration_client
    payload = {
        "nombre": "Ana",
        "email": "ana@example.com",
        "password": "secreto de prueba",
        **changes,
    }
    response = client.post("/v1/auth/register", json=payload)
    assert response.status_code == 422
    assert payload["password"] not in response.text
    assert not repository.cuentas
