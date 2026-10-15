"""Baja física, protección y tokens de Cuenta borrada."""


def test_delete_204_404_y_desaparicion(authenticated_accounts):
    client, _, rows = authenticated_accounts
    url = f"/v1/users/{rows[1]['id']}"
    response = client.delete(url)
    assert response.status_code == 204 and response.content == b""
    assert client.get(url).status_code == 404
    assert client.delete(url).status_code == 404
    assert rows[1] not in client.get("/v1/users").json()
    assert client.delete(f"/v1/users/{rows[0]['id']}").status_code == 204
    assert client.get("/v1/users/me").status_code == 401


def test_delete_sin_token_conserva_cuenta(authenticated_accounts):
    client, repository, rows = authenticated_accounts
    client.headers.pop("Authorization")
    assert client.delete(f"/v1/users/{rows[1]['id']}").status_code == 401
    assert repository.get(rows[1]["id"]) is not None
