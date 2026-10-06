"""Punto de entrada de la API."""

from fastapi import FastAPI

from src.interfaces.http.errors import register_error_handlers
from src.interfaces.http.routes.auth_routes import router as auth_router
from src.interfaces.http.routes.health_routes import router as health_router
from src.interfaces.http.routes.user_routes import router as user_router

DESCRIPTION = """
API de gestión de usuarios (proyecto g1, especificación V2).

Incluye registro, login con JWT y CRUD bajo `/v1`. Usa Authorize con tu email
y contraseña para acceder a los endpoints protegidos. Cada usuario gestiona
su perfil; los administradores también gestionan el directorio de usuarios.
"""

app = FastAPI(
    title="User Management API",
    description=DESCRIPTION,
    version="0.2.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "health", "description": "Healthchecks de la API y de MySQL"},
        {"name": "auth", "description": "Registro y login OAuth2 con JWT"},
        {"name": "users", "description": "Perfiles y administración de usuarios"},
    ],
)

app.include_router(health_router)
app.include_router(auth_router, prefix="/v1")
app.include_router(user_router, prefix="/v1")
register_error_handlers(app)
