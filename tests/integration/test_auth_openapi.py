"""Contrato público de errores, seguridad y schemas en Swagger/ReDoc."""

import httpx


def test_openapi_auth_y_cuentas_documenta_contrato(base_url):
    spec = httpx.get(f"{base_url}/openapi.json", timeout=10).json()
    paths = spec["paths"]
    login = paths["/v1/auth/login"]["post"]
    register = paths["/v1/auth/register"]["post"]
    for operation in (login, register):
        assert not operation.get("security")
        assert "403" not in operation["responses"]
    assert "401" not in register["responses"]
    assert (
        login["responses"]["401"]["headers"]["WWW-Authenticate"]["schema"]["example"]
        == "Bearer"
    )
    assert (
        login["responses"]["401"]["content"]["application/json"]["example"]["detail"]
        == "Credenciales incorrectas"
    )
    for path, methods in paths.items():
        if not path.startswith("/v1/users"):
            continue
        for operation in methods.values():
            assert operation["security"] == [{"OAuth2PasswordBearer": []}]
            for code in ("401", "403"):
                response = operation["responses"][code]
                content = response["content"]["application/json"]
                assert content["schema"]["$ref"].endswith("/ErrorResponse")
                assert isinstance(content["example"]["detail"], str)
            assert "WWW-Authenticate" in operation["responses"]["401"]["headers"]
            assert "headers" not in operation["responses"]["403"]
    listing = paths["/v1/users"]["get"]
    assert listing["responses"]["400"]["content"]["application/json"]["example"][
        "detail"
    ]
    assert {
        "q",
        "nombre",
        "email",
        "activo",
        "rol",
        "id_cliente",
        "fecha_creacion_desde",
        "fecha_creacion_hasta",
        "offset",
        "limit",
    } <= {p["name"] for p in listing["parameters"]}
    response_fields = spec["components"]["schemas"]["CuentaResponse"]["properties"]
    assert not {"password", "password_hash"} & response_fields.keys()
    patch_fields = spec["components"]["schemas"]["CuentaPatch"]["properties"]
    for field in ("nombre", "email", "password"):
        assert patch_fields[field]["type"] == "string"
        assert "default" not in patch_fields[field]
    for path in ("/docs", "/redoc"):
        page = httpx.get(f"{base_url}{path}", timeout=10)
        assert page.status_code == 200 and "/openapi.json" in page.text
