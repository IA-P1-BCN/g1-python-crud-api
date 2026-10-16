"""Autorización por rol, previa a lectura o borrado de Cuentas."""

import pytest


@pytest.mark.parametrize("rol", ["staff", "cliente"])
def test_otros_roles_no_listan_ni_borran(authenticated_accounts, rol):
    client, repository, rows = authenticated_accounts
    repository.cuentas[0].rol = rol
    for method, path in (
        ("GET", "/v1/users"),
        ("DELETE", f"/v1/users/{rows[1]['id']}"),
        ("DELETE", "/v1/users/99999"),
    ):
        result = client.request(method, path)
        assert result.status_code == 403
        assert result.json() == {"detail": "Esta operación requiere rol admin"}
        assert "www-authenticate" not in result.headers
    assert len(repository.cuentas) == 3
    assert client.get("/v1/users/me").status_code == 200


def test_rol_actual_se_relee_con_el_mismo_token(authenticated_accounts):
    client, repository, _ = authenticated_accounts
    assert client.get("/v1/users").status_code == 200
    repository.cuentas[0].rol = "cliente"
    assert client.get("/v1/users").status_code == 403
    repository.cuentas[0].rol = "admin"
    assert client.get("/v1/users").status_code == 200
    repository.cuentas[0].activo = False
    assert client.get("/v1/users").status_code == 403
