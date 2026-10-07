"""Configuración de logging de la aplicación.

Uso:

     from core.logging import setup_logging

    setup_logging()  # INFO + logs/app.log (los valores por defecto)
"""

import logging
import os
from logging.config import dictConfig

FORMATO = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
NIVELES_VALIDOS = ("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET")


def _nivel_o_info(nivel: str) -> str:
    """Devuelve el nivel en mayúsculas si es válido; `INFO` en caso contrario."""
    normalizado = (nivel or "INFO").upper()
    if normalizado not in NIVELES_VALIDOS:
        logging.getLogger(__name__).warning(
            "LOG_LEVEL desconocido %r; se usa INFO", nivel
        )
        return "INFO"
    return normalizado


def setup_logging(nivel: str = "INFO", log_file: str = "logs/app.log") -> None:
    """Configura los loggers de la aplicación (consola + fichero rotativo).

    Es idempotente: llamarla varias veces (recarga de uvicorn, tests) no
    duplica handlers.
    """
    nivel_raiz = _nivel_o_info(nivel)
    ruta_dir = os.path.dirname(log_file)
    if ruta_dir:
        os.makedirs(ruta_dir, exist_ok=True)

    handlers = {
        "consola": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "estandar",
            "level": nivel_raiz,
        },
        "fichero": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": log_file,
            "maxBytes": 1_000_000,
            "backupCount": 3,
            "encoding": "utf-8",
            "formatter": "estandar",
            "level": nivel_raiz,
        },
    }

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "estandar": {"format": FORMATO, "datefmt": "%Y-%m-%d %H:%M:%S"},
        },
        "handlers": handlers,
        "root": {"level": nivel_raiz, "handlers": ["consola", "fichero"]},
        "loggers": {
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["consola"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "WARNING",
                "handlers": ["consola"],
                "propagate": False,
            },
        },
    }
    dictConfig(config)
