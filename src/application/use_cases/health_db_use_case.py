"""Caso de uso: comprobar la base de datos y su versión de esquema."""

from src.domain.entities.health import DatabaseHealth
from src.domain.repositories.health_port import HealthRepository


def get_health_db(repository: HealthRepository) -> DatabaseHealth:
    """Hace ping a la base de datos y lee la última versión del esquema.

    Cualquier fallo de infraestructura (conexión, consulta) se traduce como
    base de datos caída, para que la capa HTTP devuelva un 503.
    """
    try:
        if not repository.ping():
            return DatabaseHealth(status="error", database="down", version=None)
        version = repository.get_latest_version()
    except Exception:  # noqa: BLE001 - cualquier fallo de infra es "caída"
        return DatabaseHealth(status="error", database="down", version=None)
    return DatabaseHealth(status="ok", database="up", version=version)
