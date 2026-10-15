"""Persistencia y login después de editar credenciales."""

from uuid import uuid4


def test_edicion_y_login_con_nueva_password(accounts_api):
    client, emails = accounts_api
    email, changed_email = (f"{uuid4().hex}@example.com" for _ in range(2))
    emails.extend([email, changed_email])
    password = "contraseña de prueba"
    created = client.post(
        "/v1/auth/register",
        json={"nombre": "Original", "email": email, "password": password},
    ).json()
    token = client.post(
        "/v1/auth/login", data={"username": email, "password": password}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    url = f"/v1/users/{created['id']}"
    result = client.put(
        url, json={"nombre": "Editada", "email": changed_email}, headers=headers
    )
    assert result.status_code == 200, result.text
    assert (
        client.post(
            "/v1/auth/login", data={"username": changed_email, "password": password}
        ).status_code
        == 200
    )
    result = client.patch(url, json={"password": " contraseña nueva "}, headers=headers)
    assert result.status_code == 200 and "password" not in result.text
    assert client.get(url, headers=headers).json() == result.json()
    assert (
        client.post(
            "/v1/auth/login", data={"username": changed_email, "password": password}
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/v1/auth/login",
            data={"username": changed_email, "password": " contraseña nueva "},
        ).status_code
        == 200
    )
