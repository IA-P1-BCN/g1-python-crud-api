"""Test de integración de GET /health/db."""

import socket

import httpx
import pytest

from config.settings import get_settings


def _mysql_disponible() -> bool:
    ajustes = get_settings()
    try:
        with socket.create_connection(
            (ajustes.mysql_host, ajustes.mysql_port), timeout=2
        ):
            return True
    except OSError:
        return False


pytestmark = pytest.mark.skipif(
    not _mysql_disponible(),
    reason="MySQL no disponible: ejecuta `task db:up && task migrate`",
)


def test_health_db_devuelve_200_y_version(base_url):
    response = httpx.get(f"{base_url}/health/db", timeout=5)
    assert response.status_code == 200
    cuerpo = response.json()
    assert cuerpo["status"] == "ok"
    assert cuerpo["database"] == "up"
    assert cuerpo["version"] == "0.1"
