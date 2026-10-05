"""Schemas de los healthchecks."""

from pydantic import BaseModel, Field


class HealthCheck(BaseModel):
    """Respuesta de GET /health."""

    status: str = Field(description="Estado de la aplicación", examples=["ok"])


class HealthDbCheck(BaseModel):
    """Respuesta de GET /health/db."""

    status: str = Field(description="Estado del healthcheck", examples=["ok", "error"])
    database: str = Field(description="Conectividad", examples=["up", "down"])
    version: str | None = Field(
        default=None,
        description="Última versión del esquema leída de la tabla `versions`",
        examples=["0.1"],
    )
