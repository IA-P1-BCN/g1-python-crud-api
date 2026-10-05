"""Test de integración de GET /health."""

import httpx


def test_health_devuelve_200(base_url):
    response = httpx.get(f"{base_url}/health", timeout=5)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
