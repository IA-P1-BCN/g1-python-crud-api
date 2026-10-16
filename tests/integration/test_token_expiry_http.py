"""Un JWT emitido por login real deja de servir cuando pasa su exp configurada."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt

from config.settings import get_settings


def test_login_respeta_entorno_y_caducidad(accounts_api, monkeypatch):
    client, emails = accounts_api
    email = f"{uuid4().hex}@example.com"
    emails.append(email)
    try:
        monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "7")
        get_settings.cache_clear()
        client.post(
            "/v1/auth/register",
            json={
                "nombre": "Caducidad",
                "email": email,
                "password": "clave de pruebas",
            },
        ).raise_for_status()
        response = client.post(
            "/v1/auth/login",
            data={
                "username": email,
                "password": "clave de pruebas",
            },
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        secret = get_settings().secret_key.get_secret_value()
        claims = jwt.decode(token, secret, algorithms=["HS256"], audience="gymflow-api")
        assert claims["exp"] - claims["iat"] == 420
        headers = {"Authorization": f"Bearer {token}"}
        assert client.get("/v1/users/me", headers=headers).status_code == 200

        # Una configuración nueva no altera el exp de tokens existentes.
        monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        get_settings.cache_clear()
        future = datetime.now(UTC) + timedelta(minutes=8)

        class FutureClock(datetime):
            @classmethod
            def now(cls, tz=None):
                return future if tz is not None else future.replace(tzinfo=None)

        monkeypatch.setattr(jwt.api_jwt, "datetime", FutureClock)
        for path in ("/v1/users/me", "/v1/clases", "/v1/export/csv?tablas=clientes"):
            response = client.get(path, headers=headers)
            assert response.status_code == 401
            assert response.headers["www-authenticate"] == "Bearer"
    finally:
        get_settings.cache_clear()
