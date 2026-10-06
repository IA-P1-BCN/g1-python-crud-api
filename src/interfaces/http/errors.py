"""Traducción de los errores del CRUD a respuestas HTTP documentadas."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.domain.errors import ConflictError, NotFoundError, RepositoryUnavailableError
from src.interfaces.http.schemas.gym_schema import ErrorResponse

CRUD_ERRORS = {
    404: {"model": ErrorResponse, "description": "Registro o referencia no encontrado"},
    409: {
        "model": ErrorResponse,
        "description": "Conflicto de datos o regla de negocio",
    },
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
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    app.add_exception_handler(NotFoundError, not_found)
    app.add_exception_handler(ConflictError, conflict)
    app.add_exception_handler(RepositoryUnavailableError, unavailable)
