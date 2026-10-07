"""Tests de la configuración de logging."""

import logging

import pytest

from core.logging import setup_logging


@pytest.fixture(autouse=True)
def restaurar_configuracion_logging():
    """Guarda la configuración global del logger y la restaura al terminar."""
    raiz = logging.getLogger()
    handlers_previos = list(raiz.handlers)
    nivel_previo = raiz.level
    yield
    for handler in list(raiz.handlers):
        if handler not in handlers_previos:
            handler.close()
    raiz.handlers = handlers_previos
    raiz.setLevel(nivel_previo)


def test_setup_logging_crea_el_fichero_y_escribe(tmp_path):
    fichero = tmp_path / "salida" / "app.log"
    setup_logging(log_file=str(fichero))

    logging.getLogger("test.prueba").info("mensaje de prueba")

    assert fichero.is_file()
    contenido = fichero.read_text(encoding="utf-8")
    assert "mensaje de prueba" in contenido
    assert "INFO" in contenido
    assert "test.prueba" in contenido


def test_el_nivel_configurado_filtra_los_mensajes(tmp_path):
    fichero = tmp_path / "app.log"
    setup_logging(nivel="WARNING", log_file=str(fichero))
    logger = logging.getLogger("test.filtro")

    logger.debug("esto no aparece")
    logger.warning("esto sí aparece")

    contenido = fichero.read_text(encoding="utf-8")
    assert "esto no aparece" not in contenido
    assert "esto sí aparece" in contenido


def test_setup_logging_no_duplica_handlers(tmp_path):
    fichero = tmp_path / "app.log"
    setup_logging(log_file=str(fichero))
    primera = len(logging.getLogger().handlers)

    setup_logging(log_file=str(fichero))

    assert primera == 2
    assert len(logging.getLogger().handlers) == primera


def test_un_nivel_desconocido_usa_info(tmp_path):
    fichero = tmp_path / "app.log"
    setup_logging(nivel="TRUCO", log_file=str(fichero))

    assert logging.getLogger().level == logging.INFO
