"""Traducción de los errores del CRUD a respuestas HTTP documentadas."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.domain.errors import ConflictError, NotFoundError, RepositoryUnavailableError
from src.interfaces.http.schemas.gym_schema import ErrorResponse

logger = logging.getLogger(__name__)

# Mensaje fijo para el cliente: el detalle real solo se escribe en el log.
INTERNAL_ERROR_MESSAGE = "Error interno del servidor"

CRUD_ERRORS = {
    404: {"model": ErrorResponse, "description": "Registro o referencia no encontrado"},
    409: {
        "model": ErrorResponse,
        "description": "Conflicto de datos o regla de negocio",
    },
    500: {"model": ErrorResponse, "description": "Error interno inesperado"},
    503: {"model": ErrorResponse, "description": "Base de datos no disponible"},
}


def register_crud_error_handlers(app: FastAPI) -> None:
    async def not_found(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    async def conflict(request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    async def unavailable(
        request: Request, exc: RepositoryUnavailableError
    ) -> JSONResponse:
        logger.error(
            "Base de datos no disponible en %s %s",
            request.method,
            request.url.path,
            exc_info=exc,
        )
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    async def unexpected(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "Error no controlado en %s %s",
            request.method,
            request.url.path,
            exc_info=exc,
        )
        return JSONResponse(status_code=500, content={"detail": INTERNAL_ERROR_MESSAGE})

    app.add_exception_handler(NotFoundError, not_found)
    app.add_exception_handler(ConflictError, conflict)
    app.add_exception_handler(RepositoryUnavailableError, unavailable)
    app.add_exception_handler(Exception, unexpected)
