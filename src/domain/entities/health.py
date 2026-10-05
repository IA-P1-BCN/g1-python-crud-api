"""Entidades de los healthchecks."""

from dataclasses import dataclass


@dataclass(frozen=True)
class HealthStatus:
    """Estado de vida de la aplicación."""

    status: str


@dataclass(frozen=True)
class DatabaseHealth:
    """Estado de la conexión a la base de datos y versión de su esquema."""

    status: str
    database: str
    version: str | None
