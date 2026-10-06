"""Respuestas de error sin datos sensibles del request ni detalles SQL."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.domain.errors import (
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RepositoryUnavailableError,
)
from src.interfaces.http.schemas.user_schema import ErrorResponse

ERROR_RESPONSES = {
    code: {"model": ErrorResponse, "description": description}
    for code, description in {
        401: "Credenciales no válidas",
        403: "Permiso insuficiente",
        404: "Usuario no encontrado",
        409: "Email duplicado",
        503: "Base de datos no disponible",
    }.items()
}


def register_error_handlers(app: FastAPI) -> None:
    async def application_error(request: Request, exc: Exception) -> JSONResponse:
        status = {
            AuthenticationError: 401,
            ForbiddenError: 403,
            NotFoundError: 404,
            ConflictError: 409,
            RepositoryUnavailableError: 503,
        }[type(exc)]
        headers = {"WWW-Authenticate": "Bearer"} if status == 401 else None
        return JSONResponse(
            status_code=status, content={"detail": str(exc)}, headers=headers
        )

    async def validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Pydantic incluye el valor recibido en `input`; puede ser una contraseña.
        detail = [
            {key: error[key] for key in ("type", "loc", "msg")}
            for error in exc.errors()
        ]
        return JSONResponse(status_code=422, content={"detail": detail})

    for error in (
        AuthenticationError,
        ForbiddenError,
        NotFoundError,
        ConflictError,
        RepositoryUnavailableError,
    ):
        app.add_exception_handler(error, application_error)
    app.add_exception_handler(RequestValidationError, validation_error)
