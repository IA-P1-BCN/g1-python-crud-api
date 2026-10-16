"""Contraseña propia verificada bajo bloqueo con persistencia real."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4


def test_perfil_propio_y_cambios_concurrentes(accounts_api):
    client, emails = accounts_api
    email, new_email = (f"{uuid4().hex}@example.com" for _ in range(2))
    emails.extend([email, new_email])
    password = "contraseña de prueba"
    created = client.post(
        "/v1/auth/register",
        json={
            "nombre": "Original",
            "email": email,
            "password": password,
        },
    ).json()
    token = client.post(
        "/v1/auth/login",
        data={
            "username": email,
            "password": password,
        },
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert (
        client.patch(
            "/v1/users/me",
            headers=headers,
            json={
                "nombre": "No guardar",
                "password": "otra contraseña",
                "current_password": "mal",
            },
        ).status_code
        == 403
    )
    assert client.get("/v1/users/me", headers=headers).json() == created
    result = client.patch(
        "/v1/users/me",
        headers=headers,
        json={
            "email": new_email,
            "nombre": "Editada",
        },
    )
    assert result.status_code == 200
    assert result.json()["rol"] == "cliente" and "password" not in result.text
    barrier = Barrier(2)

    def change(new_password):
        barrier.wait(timeout=5)
        response = client.patch(
            "/v1/users/me",
            headers=headers,
            json={
                "password": new_password,
                "current_password": password,
            },
        )
        return new_password, response.status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(change, [" nueva clave primera ", " nueva clave segunda "])
        )
    assert sorted(status for _, status in results) == [200, 403]
    for attempted, status in results:
        result = client.post(
            "/v1/auth/login",
            data={
                "username": new_email,
                "password": attempted,
            },
        )
        assert result.status_code == (200 if status == 200 else 401)
    assert (
        client.post(
            "/v1/auth/login",
            data={
                "username": new_email,
                "password": password,
            },
        ).status_code
        == 401
    )
    assert (
        client.patch(
            f"/v1/users/{created['id']}",
            headers=headers,
            json={
                "password": "otro atajo prohibido",
            },
        ).status_code
        == 403
    )
