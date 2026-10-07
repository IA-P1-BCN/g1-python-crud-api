"""Carga de las variables de entorno sensibles en `Settings`."""

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
