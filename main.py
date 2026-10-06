"""Punto de entrada de la API."""

from fastapi import FastAPI

from src.interfaces.http.routes.health_routes import router as health_router

DESCRIPTION = """
API de gestión del gimnasio (proyecto g1).

Incluye healthchecks de aplicación y de base de datos. Los endpoints de
negocio se publicarán bajo el prefijo `/v1`.
"""

app = FastAPI(
    title="API de Gestión de Gimnasio",
    description=DESCRIPTION,
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "health", "description": "Healthchecks de la API y de MySQL"}
    ],
)

app.include_router(health_router)
