"""Tests del bootstrap de `.env`: relleno, preservación y puerto MySQL."""

import pytest

from scripts import bootstrap_env

EXAMPLE = """\
# Comentario de plantilla
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=gym_db

ADMIN_PASSWORD=change-me
ADMIN_EMAIL=admin@example.com
SECRET_KEY=
LOG_LEVEL=INFO
"""

CLAVE_VALIDA = "k" * 64
PASSWORD_VALIDA = "una-clave-larga-valida"


@pytest.fixture
def entorno(tmp_path, monkeypatch):
    """Raíz temporal con plantilla y sin contenedor propio."""
    monkeypatch.setattr(bootstrap_env, "ENV_PATH", tmp_path / ".env")
    monkeypatch.setattr(bootstrap_env, "EXAMPLE_PATH", tmp_path / ".env.example")
    (tmp_path / ".env.example").write_text(EXAMPLE, encoding="utf-8")
    monkeypatch.setattr(bootstrap_env, "puertos_contenedor_propio", lambda: set())
    return tmp_path


def valores(tmp_path):
    return bootstrap_env.parsear(
        (tmp_path / ".env").read_text(encoding="utf-8")
    )


def test_crea_env_desde_cero(entorno, monkeypatch):
    monkeypatch.setattr(bootstrap_env, "puerto_libre", lambda puerto: True)

    assert bootstrap_env.main() == 0
    config = valores(entorno)

    assert len(config["SECRET_KEY"]) >= 32
    assert len(config["ADMIN_PASSWORD"]) >= 12
    assert not config["ADMIN_PASSWORD"].startswith("change-me")
    assert config["MYSQL_PORT"] == "3306"
    assert config["LOG_LEVEL"] == "INFO"


def test_rellena_env_heredado_sin_pisar(entorno, monkeypatch):
    monkeypatch.setattr(bootstrap_env, "puerto_libre", lambda puerto: True)
    (entorno / ".env").write_text(
        "MYSQL_DATABASE=mi_db\nADMIN_PASSWORD=change-me\n",
        encoding="utf-8",
    )

    bootstrap_env.main()
    config = valores(entorno)

    assert config["MYSQL_DATABASE"] == "mi_db"
    assert len(config["SECRET_KEY"]) >= 32
    assert not config["ADMIN_PASSWORD"].startswith("change-me")


def test_no_pisa_lo_ya_configurado(entorno, monkeypatch):
    monkeypatch.setattr(bootstrap_env, "puerto_libre", lambda puerto: True)
    (entorno / ".env").write_text(
        f"SECRET_KEY={CLAVE_VALIDA}\n"
        f"ADMIN_PASSWORD={PASSWORD_VALIDA}\n"
        "LOG_LEVEL=DEBUG\n",
        encoding="utf-8",
    )
    antes = valores(entorno)

    bootstrap_env.main()
    config = valores(entorno)

    assert config["SECRET_KEY"] == antes["SECRET_KEY"] == CLAVE_VALIDA
    assert config["ADMIN_PASSWORD"] == PASSWORD_VALIDA
    assert config["LOG_LEVEL"] == "DEBUG"


def test_puerto_ocupado_elige_primero_libre(entorno, monkeypatch):
    monkeypatch.setattr(
        bootstrap_env, "puerto_libre", lambda puerto: puerto != 3306
    )

    bootstrap_env.main()
    assert valores(entorno)["MYSQL_PORT"] == "3307"


def test_marcador_mayusculas_tambien_se_reemplaza(entorno, monkeypatch):
    monkeypatch.setattr(bootstrap_env, "puerto_libre", lambda puerto: True)
    (entorno / ".env").write_text(
        "ADMIN_PASSWORD=Change-Me-2024\n", encoding="utf-8"
    )

    bootstrap_env.main()
    assert valores(entorno)["ADMIN_PASSWORD"] != "Change-Me-2024"


def test_claves_extra_del_env_se_conservan(entorno, monkeypatch):
    monkeypatch.setattr(bootstrap_env, "puerto_libre", lambda puerto: True)
    (entorno / ".env").write_text(
        f"SECRET_KEY={CLAVE_VALIDA}\nEXTRA_LOCAL=valor\n", encoding="utf-8"
    )

    bootstrap_env.main()
    assert valores(entorno)["EXTRA_LOCAL"] == "valor"


def test_contenedor_propio_no_cuenta_como_ocupado(entorno, monkeypatch):
    monkeypatch.setattr(bootstrap_env, "puerto_libre", lambda puerto: False)
    monkeypatch.setattr(
        bootstrap_env, "puertos_contenedor_propio", lambda: {3306}
    )

    bootstrap_env.main()
    assert valores(entorno)["MYSQL_PORT"] == "3306"
