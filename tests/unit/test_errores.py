"""Contrato de errores de la API: formato uniforme, trazas en log y sin fugas."""

import logging

import pytest
from fastapi.testclient import TestClient

from main import app
from src.domain.errors import RepositoryUnavailableError
from src.interfaces.http.dependencies import get_gym_repository
from src.interfaces.http.errors import INTERNAL_ERROR_MESSAGE

DETALLE_INTERNO = "password=secreto-que-no-debe-salir"


@pytest.fixture
def client_sin_reraise(repository):
    """Devuelve el 500 como respuesta en lugar de relanzar la excepción."""
    app.dependency_overrides[get_gym_repository] = lambda: repository
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_gym_repository, None)


def _falla_con(monkeypatch, repository, error):
    def fail(*args):
        raise error

    monkeypatch.setattr(repository, "list", fail)


def _registros_de_error(caplog):
    return [r for r in caplog.records if r.levelno >= logging.ERROR]


def test_error_inesperado_devuelve_500_generico(
    client_sin_reraise, repository, monkeypatch
):
    _falla_con(monkeypatch, repository, RuntimeError(DETALLE_INTERNO))

    response = client_sin_reraise.get("/v1/clientes")

    assert response.status_code == 500
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"detail": INTERNAL_ERROR_MESSAGE}
    assert DETALLE_INTERNO not in response.text


def test_error_inesperado_se_registra_con_traza(
    client_sin_reraise, repository, monkeypatch, caplog
):
    caplog.set_level(logging.ERROR)
    _falla_con(monkeypatch, repository, RuntimeError(DETALLE_INTERNO))

    client_sin_reraise.get("/v1/clientes")

    registros = _registros_de_error(caplog)
    assert len(registros) == 1
    assert "GET /v1/clientes" in registros[0].getMessage()
    assert DETALLE_INTERNO in str(registros[0].exc_info[1])


def test_base_de_datos_no_disponible_se_registra(
    client_sin_reraise, repository, monkeypatch, caplog
):
    caplog.set_level(logging.ERROR)
    error = RepositoryUnavailableError("Base de datos no disponible")
    _falla_con(monkeypatch, repository, error)

    response = client_sin_reraise.get("/v1/clientes")

    assert response.status_code == 503
    assert response.json() == {"detail": "Base de datos no disponible"}
    assert len(_registros_de_error(caplog)) == 1


def test_errores_de_cliente_no_se_registran_como_error(client, caplog):
    caplog.set_level(logging.ERROR)

    response = client.get("/v1/clientes/999")

    assert response.status_code == 404
    assert _registros_de_error(caplog) == []


@pytest.mark.parametrize(
    "method,path,status",
    [("get", "/v1/no-existe", 404), ("delete", "/v1/clientes", 405)],
)
def test_ruta_o_metodo_inexistente_usa_el_mismo_formato(client, method, path, status):
    response = getattr(client, method)(path)

    assert response.status_code == status
    assert isinstance(response.json()["detail"], str)


def test_openapi_documenta_el_error_500_en_todos_los_endpoints_de_negocio(client):
    paths = client.get("/openapi.json").json()["paths"]
    operaciones = [
        operation
        for path, methods in paths.items()
        if path.startswith("/v1/")
        for operation in methods.values()
    ]

    assert operaciones
    for operation in operaciones:
        schema = operation["responses"]["500"]["content"]["application/json"]["schema"]
        assert schema["$ref"].endswith("/ErrorResponse")
