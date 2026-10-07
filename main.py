"""Punto de entrada de la API."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from config.settings import get_settings
from core.logging import setup_logging
from src.interfaces.http.errors import register_crud_error_handlers
from src.interfaces.http.routes.clase_routes import router as clase_router
from src.interfaces.http.routes.cliente_routes import router as cliente_router
from src.interfaces.http.routes.entrenador_routes import router as entrenador_router
from src.interfaces.http.routes.health_routes import router as health_router
from src.interfaces.http.routes.pago_routes import router as pago_router
from src.interfaces.http.routes.reserva_routes import router as reserva_router

settings = get_settings()
setup_logging(settings.log_level, settings.log_file)
logger = logging.getLogger(__name__)

DESCRIPTION = """
API de gestión del gimnasio (proyecto g1).

Incluye healthchecks y operaciones CRUD de clientes, entrenadores, clases,
reservas y pagos bajo `/v1`. Las reservas requieren un cliente activo con
un pago registrado y una plaza disponible en la clase.
"""


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Registra el arranque y el cierre de la aplicación."""
    logger.info("GymFlow API v%s lista", app.version)
    yield
    logger.info("GymFlow API v%s cerrada", app.version)


app = FastAPI(
    title="GymFlow API",
    description=DESCRIPTION,
    version="0.1.0",
    lifespan=lifespan,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "health", "description": "Healthchecks de la API y de MySQL"},
        {"name": "clientes", "description": "Clientes y estado de membresía"},
        {"name": "entrenadores", "description": "Instructores y especialidades"},
        {"name": "clases", "description": "Sesiones, horarios UTC y aforo"},
        {"name": "reservas", "description": "Reservas de plazas y asistencia"},
        {"name": "pagos", "description": "Registro de pagos de clientes"},
    ],
)

app.include_router(health_router)
app.include_router(cliente_router, prefix="/v1")
app.include_router(entrenador_router, prefix="/v1")
app.include_router(clase_router, prefix="/v1")
app.include_router(reserva_router, prefix="/v1")
app.include_router(pago_router, prefix="/v1")
register_crud_error_handlers(app)
