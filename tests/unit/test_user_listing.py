"""Listados, detalle, validación y orden de rutas de Cuentas."""

import pytest


def test_listado_detalle_y_404(authenticated_accounts):
    client, _, rows = authenticated_accounts
    assert client.get("/v1/users").json() == rows
    assert client.get("/v1/users", params={"offset": 1, "limit": 1}).json() == [rows[1]]
    assert client.get("/v1/users", params={"offset": 100}).json() == []
    assert client.get(f"/v1/users/{rows[1]['id']}").json() == rows[1]
    assert client.get("/v1/users/me").json() == rows[0]
    assert client.get("/v1/users/99999").status_code == 404


@pytest.mark.parametrize(
    "query", [{"offset": -1}, {"limit": 101}, {"limit": 0}, {"otro": 1}]
)
def test_query_invalida(authenticated_accounts, query):
    client, _, _ = authenticated_accounts
    assert client.get("/v1/users", params=query).status_code == 422


def test_consultas_exigen_token(registration_client):
    client, _ = registration_client
    for path in ["/v1/users", "/v1/users/1"]:
        assert client.get(path).status_code == 401
