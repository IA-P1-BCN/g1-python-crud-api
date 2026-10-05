"""Controlador del healthcheck de aplicación."""

from src.application.use_cases.health_use_case import get_health
from src.domain.entities.health import HealthStatus


def get_health_status() -> HealthStatus:
    """Ejecuta el caso de uso de vida de la aplicación."""
    return get_health()
