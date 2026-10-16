"""Todas las operaciones de negocio rechazan accesos sin identidad válida."""

from datetime import UTC, datetime, timedelta

import jwt
import pytest

from config.settings import get_settings
from main import app
from src.interfaces.http.dependencies import get_gym_repository

OPERATIONS = [
    (method, f"/v1/{resource}{suffix}")
    for resource in ("clientes", "entrenadores", "clases", "reservas", "pagos")
    for method, suffix in (
        ("GET", ""),
        ("POST", ""),
        ("GET", "/1"),
        ("PUT", "/1"),
        ("DELETE", "/1"),
    )
] + [("GET", "/v1/export/csv?tablas=clientes")]


@pytest.mark.parametrize("method,path", OPERATIONS)
@pytest.mark.parametrize("credential", ["missing", "invalid", "expired"])
def test_todas_las_operaciones_exigen_jwt(
    registration_client, method, path, credential
):
    client, _ = registration_client
    headers = {}
    if credential == "invalid":
        headers["Authorization"] = "Bearer invalid-token"
    if credential == "expired":
        now = datetime.now(UTC)
        token = jwt.encode(
            {
                "sub": "1",
                "iat": now - timedelta(hours=2),
                "exp": now - timedelta(hours=1),
                "iss": "gymflow",
                "aud": "gymflow-api",
            },
            get_settings().secret_key.get_secret_value(),
            algorithm="HS256",
        )
        headers["Authorization"] = f"Bearer {token}"
    response = client.request(method, path, headers=headers, json={})
    assert response.status_code == 401, response.text
    assert response.headers["www-authenticate"] == "Bearer"


def test_identidad_se_revalida_en_el_gimnasio(authenticated_accounts, repository):
    client, accounts, _ = authenticated_accounts
    app.dependency_overrides[get_gym_repository] = lambda: repository
    try:
        assert client.get("/v1/clases").status_code == 200
        accounts.cuentas[0].activo = False
        denied = client.get("/v1/clases")
        assert denied.status_code == 403
        assert "www-authenticate" not in denied.headers
        accounts.cuentas.clear()
        assert client.get("/v1/clases").status_code == 401
    finally:
        app.dependency_overrides.pop(get_gym_repository, None)
