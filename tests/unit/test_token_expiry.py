"""Duración configurable y rechazo de valores que no definen una sesión válida."""

import jwt
import pytest
from pydantic import ValidationError

from config.settings import Settings
from src.infrastructure.security.tokens import JwtAccessTokens


@pytest.mark.parametrize("minutes", [1, 7, 30, 1440])
def test_duracion_desde_entorno(monkeypatch, minutes):
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(minutes))
    settings = Settings(_env_file=None)
    secret = settings.secret_key.get_secret_value()
    token = JwtAccessTokens(secret, settings.access_token_expire_minutes).issue(1)
    claims = jwt.decode(token, secret, algorithms=["HS256"], audience="gymflow-api")
    assert claims["exp"] - claims["iat"] == minutes * 60


def test_duracion_por_defecto(monkeypatch):
    monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_MINUTES", raising=False)
    assert Settings(_env_file=None).access_token_expire_minutes == 30


@pytest.mark.parametrize("value", ["0", "-1", "1.5", "incorrecto", "1441", ""])
def test_rechaza_configuracion_invalida(monkeypatch, value):
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", value)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


@pytest.mark.parametrize("value", [0, -1, 1.5, 1441, True])
def test_adaptador_rechaza_duracion_invalida(value):
    with pytest.raises(ValueError):
        JwtAccessTokens("test-secret-with-at-least-32-characters", value)
