"""Contrato unitario de los endpoints de usuarios, autenticación y permisos."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta

import jwt
import pytest

from src.domain.errors import RepositoryUnavailableError

PASSWORD = "Example-Password-1234"
PROFILE = {"name": " Ana García ", "email": " ANA@EXAMPLE.COM ", "password": PASSWORD}
TEST_SECRET = "unit-test-secret-only-000000000000000000000000"


def register(client, **changes):
    response = client.post("/v1/auth/register", json=PROFILE | changes)
    assert response.status_code == 201, response.text
    return response.json()


def login(client, email="ana@example.com", password=PASSWORD):
    return client.post("/v1/auth/login", data={"username": email, "password": password})


def user_headers(client):
    response = login(client)
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_registro_login_y_perfil(client, repository, passwords):
    user = register(client)
    assert user["name"] == "Ana García"
    assert user["email"] == "ana@example.com"
    assert user["role"] == "user"
    assert user["is_active"] is True
    assert set(user) == {"id", "name", "email", "created_at", "is_active", "role"}
    stored = repository.get(user["id"])
    assert stored.password_hash.startswith("$argon2")
    assert stored.password_hash != PASSWORD
    assert passwords.verify(PASSWORD, stored.password_hash)
    response = login(client, " ANA@example.com ")
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["expires_in"] == 1800
    headers = user_headers(client)
    assert client.get("/v1/users/me", headers=headers).json() == user
    assert client.get(f"/v1/users/{user['id']}", headers=headers).json() == user


def test_crud_admin_y_paginacion(client, admin_headers):
    created = client.post("/v1/users", json=PROFILE, headers=admin_headers)
    assert created.status_code == 201
    user = created.json()
    path = f"/v1/users/{user['id']}"
    assert client.get(path, headers=admin_headers).json() == user
    listed = client.get(
        "/v1/users", params={"offset": 1, "limit": 1}, headers=admin_headers
    )
    assert listed.status_code == 200
    assert listed.json() == [user]
    updated = client.put(
        path,
        headers=admin_headers,
        json={
            "name": "Nombre nuevo",
            "email": "nuevo@example.com",
            "is_active": True,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["created_at"] == user["created_at"]
    assert updated.json()["name"] == "Nombre nuevo"
    assert client.get(path, headers=admin_headers).json() == updated.json()
    deleted = client.delete(path, headers=admin_headers)
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(path, headers=admin_headers).status_code == 404
    assert client.delete(path, headers=admin_headers).status_code == 404


def test_propietario_modifica_y_borra_su_perfil(client):
    user = register(client)
    headers = user_headers(client)
    path = f"/v1/users/{user['id']}"
    response = client.put(
        path,
        headers=headers,
        json={
            "name": "Ana nueva",
            "email": user["email"],
            "is_active": True,
        },
    )
    assert response.status_code == 200
    assert client.delete(path, headers=headers).status_code == 204
    assert client.get("/v1/users/me", headers=headers).status_code == 401


@pytest.mark.parametrize(
    "method,path",
    [
        ("get", "/v1/users"),
        ("post", "/v1/users"),
        ("get", "/v1/users/me"),
        ("get", "/v1/users/1"),
        ("put", "/v1/users/1"),
        ("delete", "/v1/users/1"),
    ],
)
def test_exige_token(client, method, path):
    response = client.request(method, path)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "method,path",
    [
        ("get", "/v1/users"),
        ("post", "/v1/users"),
        ("get", "/v1/users/1"),
        ("put", "/v1/users/1"),
        ("delete", "/v1/users/1"),
        ("get", "/v1/users/999"),
    ],
)
def test_usuario_no_administra_otros(client, method, path):
    register(client)
    kwargs = {}
    if method == "post":
        kwargs["json"] = PROFILE | {"email": "otro@example.com"}
    if method == "put":
        kwargs["json"] = {
            "name": "Otro",
            "email": "otro@example.com",
            "is_active": True,
        }
    response = client.request(method, path, headers=user_headers(client), **kwargs)
    assert response.status_code == 403


def test_email_duplicado_en_registro_y_actualizacion(client, admin_headers):
    user = register(client)
    assert client.post("/v1/auth/register", json=PROFILE).status_code == 409
    response = client.put(
        f"/v1/users/{user['id']}",
        headers=admin_headers,
        json={
            "name": "Cambio",
            "email": "ADMIN@example.com",
            "is_active": True,
        },
    )
    assert response.status_code == 409
    assert client.get(f"/v1/users/{user['id']}", headers=admin_headers).json() == user


def test_login_no_revela_si_existe_la_cuenta(client, repository):
    user = register(client)
    wrong = login(client, password="password incorrecto")
    unknown = login(client, email="missing@example.com")
    repository.update(replace(repository.get(user["id"]), is_active=False))
    inactive = login(client)
    assert [response.status_code for response in (wrong, unknown, inactive)] == [
        401
    ] * 3
    assert wrong.json() == unknown.json() == inactive.json()


def test_cambio_password_revoca_token_y_password_anterior(client):
    user = register(client)
    headers = user_headers(client)
    new_password = "Replacement-Password-5678"
    updated = client.put(
        f"/v1/users/{user['id']}",
        headers=headers,
        json={
            "name": user["name"],
            "email": user["email"],
            "is_active": True,
            "password": new_password,
        },
    )
    assert updated.status_code == 200
    assert PASSWORD not in updated.text and new_password not in updated.text
    assert client.get("/v1/users/me", headers=headers).status_code == 401
    assert login(client).status_code == 401
    assert login(client, password=new_password).status_code == 200


def test_reactivar_no_revalida_tokens_antiguos(client, admin_headers):
    user = register(client)
    headers = user_headers(client)
    data = {"name": user["name"], "email": user["email"], "is_active": False}
    path = f"/v1/users/{user['id']}"
    assert client.put(path, headers=admin_headers, json=data).status_code == 200
    assert client.get("/v1/users/me", headers=headers).status_code == 401
    assert (
        client.put(
            path, headers=admin_headers, json=data | {"is_active": True}
        ).status_code
        == 200
    )
    assert client.get("/v1/users/me", headers=headers).status_code == 401
    assert login(client).status_code == 200


@pytest.mark.parametrize(
    "changes",
    [
        {"name": " "},
        {"name": "x" * 101},
        {"email": "incorrecto"},
        {"password": "Short-123"},
        {"password": "x" * 129},
        {"role": "admin"},
        {"password_hash": "hash inyectado"},
        {"is_active": False},
    ],
)
def test_valida_registro_sin_reflejar_password(client, changes):
    data = PROFILE | changes
    response = client.post("/v1/auth/register", json=data)
    assert response.status_code == 422
    assert data["password"] not in response.text
    assert all("input" not in error for error in response.json()["detail"])


def test_no_permite_escalar_rol_ni_put_incompleto(client):
    user = register(client)
    headers = user_headers(client)
    path = f"/v1/users/{user['id']}"
    assert client.put(path, headers=headers, json={"name": "Otro"}).status_code == 422
    assert (
        client.put(
            path,
            headers=headers,
            json={
                "name": user["name"],
                "email": user["email"],
                "is_active": True,
                "role": "admin",
            },
        ).status_code
        == 422
    )


@pytest.mark.parametrize(
    "variant",
    ["expired", "bad_signature", "none", "missing_exp", "bad_version", "malformed"],
)
def test_rechaza_jwt_invalidos(client, variant):
    user = register(client)
    now = datetime.now(UTC)
    payload = {
        "sub": str(user["id"]),
        "iat": now,
        "exp": now + timedelta(minutes=1),
        "ver": 0,
        "iss": "g1-user-api",
        "aud": "g1-user-api",
    }
    secret, algorithm = TEST_SECRET, "HS256"
    if variant == "expired":
        payload["iat"] = now - timedelta(minutes=2)
        payload["exp"] = now - timedelta(minutes=1)
    elif variant == "bad_signature":
        secret = "different-secret-for-test-000000000000000000"
    elif variant == "none":
        secret, algorithm = "", "none"
    elif variant == "missing_exp":
        del payload["exp"]
    elif variant == "bad_version":
        payload["ver"] = "zero"
    token = (
        "invalid.token.value"
        if variant == "malformed"
        else jwt.encode(payload, secret, algorithm=algorithm)
    )
    response = client.get("/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert token not in response.text


def test_base_de_datos_no_disponible(client, repository, monkeypatch):
    def unavailable(*args):
        raise RepositoryUnavailableError("Base de datos no disponible")

    monkeypatch.setattr(repository, "get_by_email", unavailable)
    response = login(client)
    assert response.status_code == 503
    assert response.json() == {"detail": "Base de datos no disponible"}


def test_openapi_y_authorize(client):
    spec = client.get("/openapi.json").json()
    assert (
        spec["components"]["securitySchemes"]["OAuth2PasswordBearer"]["flows"][
            "password"
        ]["tokenUrl"]
        == "/v1/auth/login"
    )
    expected = {
        "/v1/auth/register": {"post": "201"},
        "/v1/auth/login": {"post": "200"},
        "/v1/users/me": {"get": "200"},
        "/v1/users": {"get": "200", "post": "201"},
        "/v1/users/{user_id}": {"get": "200", "put": "200", "delete": "204"},
    }
    for path, methods in expected.items():
        for method, code in methods.items():
            operation = spec["paths"][path][method]
            assert operation["summary"] and operation["tags"]
            assert code in operation["responses"]
            if path.startswith("/v1/users"):
                assert operation["security"] == [{"OAuth2PasswordBearer": []}]
    output = spec["components"]["schemas"]["UserResponse"]["properties"]
    assert not {"password", "password_hash", "token_version"} & output.keys()
    assert spec["components"]["schemas"]["UserCreate"]["properties"]["password"][
        "writeOnly"
    ]
