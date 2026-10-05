"""Caso de uso: comprobar que la aplicación está viva."""

from src.domain.entities.health import HealthStatus


def get_health() -> HealthStatus:
    """Devuelve el estado de vida de la aplicación."""
    return HealthStatus(status="ok")
