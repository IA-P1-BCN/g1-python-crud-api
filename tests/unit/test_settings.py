"""Carga de las variables de entorno sensibles en `Settings`."""

import pytest
from pydantic import ValidationError

from config.settings import Settings

SECRETO = "s3creto-de-prueba"


def test_admin_password_se_lee_del_entorno(monkeypatch):
    monkeypatch.setenv("ADMIN_PASSWORD", SECRETO)

    ajustes = Settings(_env_file=None)

    assert ajustes.admin_password.get_secret_value() == SECRETO


def test_admin_password_no_se_filtra_en_repr_ni_str(monkeypatch):
    monkeypatch.setenv("ADMIN_PASSWORD", SECRETO)

    ajustes = Settings(_env_file=None)

    assert SECRETO not in repr(ajustes)
    assert SECRETO not in str(ajustes.admin_password)


def test_admin_password_es_opcional(monkeypatch):
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    ajustes = Settings(_env_file=None)

    assert ajustes.admin_password is None


def test_error_de_configuracion_no_imprime_secretos():
    with pytest.raises(ValidationError) as error:
        Settings(
            _env_file=None,
            secret_key="clave-corta",
            admin_password="password-admin-no-publicar",
        )
    assert "clave-corta" not in str(error.value)
    assert "password-admin-no-publicar" not in str(error.value)
