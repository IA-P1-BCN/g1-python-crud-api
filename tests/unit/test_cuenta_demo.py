"""La migración de la cuenta demo guarda solo el hash Argon2id."""

import importlib.util
from pathlib import Path

from src.infrastructure.security.passwords import Argon2PasswordHasher

RUTA = Path("migrations/versions/ca6c9ed6b7e8_inserta_cuenta_demo.py")
PASSWORD = "Demo56789012"


def _migracion():
    spec = importlib.util.spec_from_file_location("cuenta_demo", RUTA)
    modulo = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(modulo)
    return modulo


def test_hash_de_la_cuenta_demo_verifica_la_contrasena_publica():
    migracion = _migracion()
    assert Argon2PasswordHasher().verify(PASSWORD, migracion.PASSWORD_HASH)
    assert PASSWORD not in RUTA.read_text()
    assert migracion.EMAIL == "demo@gymflow.com"
