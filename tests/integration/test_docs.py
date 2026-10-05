"""Tests de integración de la documentación Swagger/OpenAPI."""

import httpx


def test_swagger_ui_disponible(base_url):
    response = httpx.get(f"{base_url}/docs", timeout=5)
    assert response.status_code == 200
    assert "swagger" in response.text.lower()


def test_openapi_incluye_los_healthchecks(base_url):
    response = httpx.get(f"{base_url}/openapi.json", timeout=5)
    assert response.status_code == 200
    rutas = response.json()["paths"]
    assert "/health" in rutas
    assert "/health/db" in rutas
