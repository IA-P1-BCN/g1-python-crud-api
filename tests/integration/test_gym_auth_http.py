"""Autenticación y contrato OpenAPI sobre el servidor HTTP vivo (#105)."""

import httpx


def test_todo_el_negocio_declara_y_exige_seguridad(base_url):
    with httpx.Client(base_url=base_url, timeout=10) as client:
        spec = client.get("/openapi.json").json()
        for path, methods in spec["paths"].items():
            if not path.startswith("/v1/") or path.startswith("/v1/auth/"):
                for operation in methods.values():
                    assert not operation.get("security")
                continue
            for method, operation in methods.items():
                assert operation["security"] == [{"OAuth2PasswordBearer": []}]
                assert {"401", "403"} <= operation["responses"].keys()
                url = path
                for parameter in operation.get("parameters", []):
                    if parameter["in"] == "path":
                        url = url.replace("{" + parameter["name"] + "}", "1")
                response = client.request(method, url, json={})
                assert response.status_code == 401, (method, url, response.text)
                assert response.headers["www-authenticate"] == "Bearer"
        assert client.get("/health").status_code == 200
        assert client.get("/health/db").status_code in (200, 503)
        for path in ("/docs", "/redoc"):
            assert client.get(path).status_code == 200
