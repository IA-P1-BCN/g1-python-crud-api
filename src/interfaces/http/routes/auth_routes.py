"""Registro público y login OAuth2 Password Flow."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from src.interfaces.http.controllers import user_controller as controller
from src.interfaces.http.dependencies import UseCases
from src.interfaces.http.errors import ERROR_RESPONSES
from src.interfaces.http.schemas.user_schema import (
    TokenResponse,
    UserCreate,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"], responses=ERROR_RESPONSES)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Registra un usuario activo",
)
def register(data: UserCreate, use_cases: UseCases) -> UserResponse:
    return controller.register(use_cases, data)


@router.post(
    "/login", response_model=TokenResponse, summary="Inicia sesión y obtiene un JWT"
)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    use_cases: UseCases,
    response: Response,
) -> TokenResponse:
    """Envía el email en username y la contraseña en password como formulario."""
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return controller.login(use_cases, form.username, form.password)
