"""La baja de Cuenta conserva al Cliente vinculado en MySQL."""

from uuid import uuid4

from src.infrastructure.database.engine import SessionLocal
from src.infrastructure.database.models import ClienteRecord, CuentaRecord


def test_baja_fisica_conserva_cliente(accounts_api):
    client, emails = accounts_api
    email = f"{uuid4().hex}@example.com"
    emails.append(email)
    password = "contraseña de prueba"
    cuenta = client.post(
        "/v1/auth/register",
        json={
            "nombre": "Baja",
            "email": email,
            "password": password,
            "crear_cliente": True,
        },
    ).json()
    with SessionLocal.begin() as session:
        session.get(CuentaRecord, cuenta["id"]).rol = "admin"
    token = client.post(
        "/v1/auth/login", data={"username": email, "password": password}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete(f"/v1/users/{cuenta['id']}", headers=headers)
    assert response.status_code == 204 and response.content == b""
    with SessionLocal() as session:
        assert session.get(CuentaRecord, cuenta["id"]) is None
        assert session.get(ClienteRecord, cuenta["id_cliente"]) is not None
    assert client.get("/v1/users/me", headers=headers).status_code == 401
