"""Los permisos se comprueban sobre roles persistidos y HTTP real."""

from uuid import uuid4

from src.infrastructure.database.engine import SessionLocal
from src.infrastructure.database.models import CuentaRecord


def test_roles_contra_mysql(accounts_api, gym_admin_headers):
    client, emails = accounts_api
    email = f"{uuid4().hex}@example.com"
    emails.append(email)
    cuenta = client.post(
        "/v1/auth/register",
        json={"nombre": "Socio", "email": email, "password": "clave de pruebas"},
    ).json()
    token = client.post(
        "/v1/auth/login", data={"username": email, "password": "clave de pruebas"}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    for role in ("cliente", "staff", "admin", "cliente"):
        with SessionLocal.begin() as session:
            session.get(CuentaRecord, cuenta["id"]).rol = role
        response = client.get("/v1/users", headers=headers)
        assert response.status_code == (200 if role == "admin" else 403)
        if role != "admin":
            assert (
                client.delete(f"/v1/users/{cuenta['id']}", headers=headers).status_code
                == 403
            )
            assert client.get("/v1/users/me", headers=headers).status_code == 200
    assert (
        client.delete(
            f"/v1/users/{cuenta['id']}", headers=gym_admin_headers
        ).status_code
        == 204
    )
    assert client.get("/v1/users/me", headers=headers).status_code == 401
