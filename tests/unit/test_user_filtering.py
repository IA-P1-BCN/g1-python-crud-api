"""Validación de filtros de Cuenta y conversión al contrato de dominio."""

import pytest

from src.interfaces.http.schemas.list_query import CuentaQuery


@pytest.mark.parametrize(
    "params",
    [
        {"activo": "quizá"},
        {"rol": "root"},
        {"id_cliente": 0},
        {"fecha_creacion_desde": "2026-10-14T10:00:00Z"},
        {"q": " "},
        {"password_hash": "x"},
        {"fecha_creacion_hasta": "ayer"},
    ],
)
def test_filtros_invalidos_422(authenticated_accounts, params):
    client, _, _ = authenticated_accounts
    assert client.get("/v1/users", params=params).status_code == 422


def test_intervalo_400_antes_de_listar(authenticated_accounts, monkeypatch):
    client, repository, _ = authenticated_accounts

    def unexpected(*args):
        pytest.fail("No debe consultar el listado")

    monkeypatch.setattr(repository, "list", unexpected)
    response = client.get(
        "/v1/users",
        params={
            "fecha_creacion_desde": "2026-10-15T00:00:00",
            "fecha_creacion_hasta": "2026-10-14T00:00:00",
        },
    )
    assert response.status_code == 400


def test_false_y_campos_tipados_se_conservan():
    query = CuentaQuery(
        activo=False,
        rol="staff",
        id_cliente=2,
        nombre="Ana",
        email="example",
        q="búsqueda",
    )
    filters = query.to_filters()
    assert filters.equals == (("activo", False), ("rol", "staff"), ("id_cliente", 2))
    assert filters.contains == (("nombre", "Ana"), ("email", "example"))
    assert filters.search == "búsqueda"
