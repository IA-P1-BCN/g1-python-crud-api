"""OAuth2, firma JWT, claims y errores indistinguibles de credenciales."""

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from pydantic import ValidationError

from config.settings import Settings, get_settings
from src.domain.errors import AuthenticationError
from src.infrastructure.security.tokens import JwtAccessTokens


def test_login_y_errores_genericos(registration_client):
    client, repository = registration_client
    password = " contraseña literal "
    created = client.post(
        "/v1/auth/register",
        json={"nombre": "Ana", "email": "ana@example.com", "password": password},
    ).json()
    response = client.post(
        "/v1/auth/login", data={"username": "ANA@example.com", "password": password}
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    tokens = JwtAccessTokens(get_settings().secret_key.get_secret_value())
    assert tokens.subject(response.json()["access_token"]) == created["id"]
    errors = []
    for email, candidate in [
        ("nadie@example.com", password),
        ("ana@example.com", "incorrecta"),
    ]:
        result = client.post(
            "/v1/auth/login", data={"username": email, "password": candidate}
        )
        assert result.status_code == 401
        assert result.headers["www-authenticate"] == "Bearer"
        errors.append(result.json())
    repository.cuentas[0].activo = False
    result = client.post(
        "/v1/auth/login", data={"username": "ana@example.com", "password": password}
    )
    assert result.status_code == 401
    assert result.json() == errors[0] == errors[1]


@pytest.mark.parametrize(
    "change",
    [
        "expired",
        "missing-exp",
        "bad-signature",
        "bad-algorithm",
        "bad-issuer",
        "bad-audience",
        "bad-sub",
        "future-iat",
    ],
)
def test_jwt_rechaza_tokens_invalidos(change):
    secret = "test-jwt-secret-with-at-least-32-characters-and-extra-test-length"
    tokens = JwtAccessTokens(secret)
    now = datetime.now(UTC)
    claims = {
        "sub": "1",
        "iat": now,
        "exp": now + timedelta(minutes=30),
        "iss": "gymflow",
        "aud": "gymflow-api",
    }
    signing_secret, algorithm = secret, "HS256"
    if change == "expired":
        claims["exp"] = now - timedelta(seconds=1)
    elif change == "missing-exp":
        del claims["exp"]
    elif change == "bad-signature":
        signing_secret = "another-test-secret-with-at-least-32-characters"
    elif change == "bad-algorithm":
        algorithm = "HS384"
    elif change == "bad-issuer":
        claims["iss"] = "otro"
    elif change == "bad-audience":
        claims["aud"] = "otro"
    elif change == "bad-sub":
        claims["sub"] = "0"
    else:
        claims["iat"] = now + timedelta(minutes=5)
    with pytest.raises(AuthenticationError):
        tokens.subject(jwt.encode(claims, signing_secret, algorithm=algorithm))


def test_openapi_password_flow_publico(registration_client):
    client, _ = registration_client
    spec = client.get("/openapi.json").json()
    scheme = spec["components"]["securitySchemes"]["OAuth2PasswordBearer"]
    assert scheme["flows"]["password"]["tokenUrl"] == "v1/auth/login"
    for path in ["/v1/auth/login", "/v1/auth/register"]:
        assert not spec["paths"][path]["post"].get("security")
    assert (
        "application/x-www-form-urlencoded"
        in spec["paths"]["/v1/auth/login"]["post"]["requestBody"]["content"]
    )


@pytest.mark.parametrize("secret", [None, "corta", ""])
def test_jwt_exige_secret_key(secret, monkeypatch):
    if secret is None:
        monkeypatch.delenv("SECRET_KEY", raising=False)
    else:
        monkeypatch.setenv("SECRET_KEY", secret)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
