"""JWT y perfil real, releyendo el estado de Cuenta en MySQL."""

from uuid import uuid4

from src.infrastructure.database.engine import SessionLocal
from src.infrastructure.database.models import CuentaRecord


def test_perfil_y_desactivacion_persistida(accounts_api):
    client, emails = accounts_api
    email = f"{uuid4().hex}@example.com"
    emails.append(email)
    password = "contraseña de prueba"
    cuenta = client.post(
        "/v1/auth/register",
        json={"nombre": "Perfil", "email": email, "password": password},
    ).json()
    token = client.post(
        "/v1/auth/login", data={"username": email, "password": password}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/v1/users/me", headers=headers).json() == cuenta
    with SessionLocal.begin() as session:
        session.get(CuentaRecord, cuenta["id"]).activo = False
    assert client.get("/v1/users/me", headers=headers).status_code == 403
    with SessionLocal.begin() as session:
        session.delete(session.get(CuentaRecord, cuenta["id"]))
    assert client.get("/v1/users/me", headers=headers).status_code == 401
