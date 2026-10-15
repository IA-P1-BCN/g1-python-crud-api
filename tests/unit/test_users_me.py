"""Perfil con identidad actual y respuesta pública."""

from datetime import UTC, datetime, timedelta

import jwt
import pytest

from config.settings import get_settings


def test_me_y_cuenta_inactiva_o_borrada(registration_client):
    client, repository = registration_client
    data = {
        "nombre": "Ana",
        "email": "ana@example.com",
        "password": "contraseña de prueba",
    }
    cuenta = client.post("/v1/auth/register", json=data).json()
    token = client.post(
        "/v1/auth/login", data={"username": data["email"], "password": data["password"]}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    result = client.get("/v1/users/me", headers=headers)
    assert result.status_code == 200 and result.json() == cuenta
    assert "password" not in result.text
    repository.cuentas[0].activo = False
    assert client.get("/v1/users/me", headers=headers).status_code == 403
    repository.cuentas.clear()
    assert client.get("/v1/users/me", headers=headers).status_code == 401


@pytest.mark.parametrize("header", [None, "Bearer no-valido", "Basic abc", "Bearer"])
def test_me_rechaza_credenciales_ausentes_o_invalidas(registration_client, header):
    client, _ = registration_client
    response = client.get(
        "/v1/users/me", headers={"Authorization": header} if header else {}
    )
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_rechaza_token_expirado(registration_client):
    client, _ = registration_client
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": "1",
            "iat": now - timedelta(hours=2),
            "exp": now - timedelta(hours=1),
            "iss": "gymflow",
            "aud": "gymflow-api",
        },
        get_settings().secret_key.get_secret_value(),
        algorithm="HS256",
    )
    assert (
        client.get(
            "/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        ).status_code
        == 401
    )
