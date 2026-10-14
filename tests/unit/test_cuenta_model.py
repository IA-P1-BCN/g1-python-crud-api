"""Contratos de hash y secretos sin acceso a MySQL."""

import pytest

from config.settings import Settings
from scripts.seed_accounts import validate_admin_password
from src.domain.entities.cuenta import Cuenta
from src.infrastructure.security.passwords import Argon2PasswordHasher


def test_argon2_verifica_y_sala_cada_hash():
    hasher = Argon2PasswordHasher()
    password = "contraseña de prueba"
    first, second = hasher.hash(password), hasher.hash(password)
    assert first.startswith("$argon2id$")
    assert first != second
    assert hasher.verify(password, first)
    assert not hasher.verify("incorrecta", first)
    assert not hasher.verify(password, "hash-no-valido")
    assert first not in repr(
        Cuenta(nombre="Ana", email="ana@example.com", password_hash=first)
    )


def test_secret_key_no_aparece_en_repr(monkeypatch):
    secret = "clave-de-prueba-solo-configuracion"
    monkeypatch.setenv("SECRET_KEY", secret)
    settings = Settings(_env_file=None)
    assert settings.secret_key.get_secret_value() == secret
    assert secret not in repr(settings)


@pytest.mark.parametrize(
    "password", [None, "change-me", "change-me-password", "corta", "x" * 129]
)
def test_seed_rechaza_password_ausente_o_marcador(password):
    with pytest.raises(ValueError):
        validate_admin_password(password)
