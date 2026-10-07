"""Rutas de healthcheck."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.domain.repositories.health_port import HealthRepository
from src.infrastructure.repositories.health_repository import get_health_repository
from src.interfaces.http.controllers import health_controller, health_db_controller
from src.interfaces.http.schemas.health_schema import HealthCheck, HealthDbCheck

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthCheck, summary="Comprueba que la API vive")
def health() -> HealthCheck:
    """Devuelve 200 si la aplicación responde."""
    estado = health_controller.get_health_status()
    return HealthCheck(status=estado.status)


@router.get(
    "/health/db",
    response_model=HealthDbCheck,
    summary="Comprueba MySQL y su versión de esquema",
    responses={503: {"description": "Base de datos no disponible"}},
)
def health_db(
    repository: Annotated[HealthRepository, Depends(get_health_repository)],
) -> HealthDbCheck:
    """Devuelve 200 con la versión del esquema o 503 si MySQL no responde."""
    estado = health_db_controller.get_database_health(repository)
    cuerpo = HealthDbCheck(
        status=estado.status, database=estado.database, version=estado.version
    )
    if estado.database != "up":
        return JSONResponse(status_code=503, content=cuerpo.model_dump(mode="json"))
    return cuerpo
