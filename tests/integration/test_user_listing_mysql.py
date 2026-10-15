"""Lectura protegida por HTTP contra la persistencia real."""

from uuid import uuid4


def test_listado_y_detalle_real(accounts_api):
    client, emails = accounts_api
    email = f"{uuid4().hex}@example.com"
    emails.append(email)
    cuenta = client.post(
        "/v1/auth/register",
        json={"nombre": "Listado", "email": email, "password": "contraseña de prueba"},
    ).json()
    token = client.post(
        "/v1/auth/login", data={"username": email, "password": "contraseña de prueba"}
    ).json()["access_token"]
    assert client.get("/v1/users").status_code == 401
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get(f"/v1/users/{cuenta['id']}", headers=headers).json() == cuenta
    result = client.get("/v1/users", params={"limit": 100}, headers=headers)
    assert result.status_code == 200
    ids = [row["id"] for row in result.json()]
    assert ids == sorted(ids) and len(ids) <= 100
    assert "password" not in result.text
    assert client.get("/v1/users/2147483647", headers=headers).status_code == 404
