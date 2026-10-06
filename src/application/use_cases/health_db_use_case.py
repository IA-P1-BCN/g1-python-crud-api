"""Caso de uso: comprobar la base de datos y su versión de esquema."""

import logging

from src.domain.entities.health import DatabaseHealth
from src.domain.repositories.health_port import HealthRepository

logger = logging.getLogger(__name__)


def get_health_db(repository: HealthRepository) -> DatabaseHealth:
    """Hace ping a la base de datos y lee la última versión del esquema.

    Cualquier fallo de infraestructura (conexión, consulta) se traduce como
    base de datos caída, para que la capa HTTP devuelva un 503.
    """
    try:
        if not repository.ping():
            logger.warning("health/db: ping de MySQL sin respuesta")
            return DatabaseHealth(status="error", database="down", version=None)
        version = repository.get_latest_version()
    except Exception:  # cualquier fallo de infraestructura es "caída"
        logger.exception("health/db: fallo consultando MySQL")
        return DatabaseHealth(status="error", database="down", version=None)
    logger.info("health/db: MySQL disponible (esquema %s)", version)
    return DatabaseHealth(status="ok", database="up", version=version)
