"""Login por HTTP real con contraseña contrastada contra MySQL."""

from uuid import uuid4

from config.settings import get_settings
from src.infrastructure.database.engine import SessionLocal
from src.infrastructure.database.models import CuentaRecord
from src.infrastructure.security.tokens import JwtAccessTokens


def test_login_real_cuenta_activa_e_inactiva(accounts_api):
    client, emails = accounts_api
    email = f"{uuid4().hex}@example.com"
    emails.append(email)
    password = "contraseña de integración"
    created = client.post(
        "/v1/auth/register",
        json={"nombre": "Cuenta login", "email": email, "password": password},
    )
    assert created.status_code == 201
    response = client.post(
        "/v1/auth/login", data={"username": email, "password": password}
    )
    assert response.status_code == 200, response.text
    assert (
        JwtAccessTokens(get_settings().secret_key.get_secret_value()).subject(
            response.json()["access_token"]
        )
        == created.json()["id"]
    )
    with SessionLocal.begin() as session:
        session.get(CuentaRecord, created.json()["id"]).activo = False
    assert (
        client.post(
            "/v1/auth/login", data={"username": email, "password": password}
        ).status_code
        == 401
    )
