"""Controlador del healthcheck de base de datos."""

from src.application.use_cases.health_db_use_case import get_health_db
from src.domain.entities.health import DatabaseHealth
from src.domain.repositories.health_port import HealthRepository


def get_database_health(repository: HealthRepository) -> DatabaseHealth:
    """Ejecuta el caso de uso de salud de la base de datos."""
    return get_health_db(repository)
