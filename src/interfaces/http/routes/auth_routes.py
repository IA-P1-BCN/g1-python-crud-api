"""Registro y autenticación públicos de Cuentas."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.interfaces.http.controllers.auth_controller import AuthController
from src.interfaces.http.controllers.cuenta_controller import CuentaController
from src.interfaces.http.dependencies import get_auth_controller, get_cuenta_controller
from src.interfaces.http.errors import CRUD_ERRORS
from src.interfaces.http.schemas.auth_schema import TokenResponse
from src.interfaces.http.schemas.cuenta_schema import CuentaRegister, CuentaResponse
from src.interfaces.http.schemas.gym_schema import ErrorResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    summary="Registrar una Cuenta",
    response_model=CuentaResponse,
    status_code=201,
    responses=CRUD_ERRORS,
)
def register(
    data: CuentaRegister,
    controller: Annotated[CuentaController, Depends(get_cuenta_controller)],
) -> CuentaResponse:
    return controller.register(data)


@router.post(
    "/login",
    summary="Iniciar sesión con email y contraseña",
    response_model=TokenResponse,
    responses={
        **CRUD_ERRORS,
        401: {"model": ErrorResponse, "description": "Credenciales incorrectas"},
    },
)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    controller: Annotated[AuthController, Depends(get_auth_controller)],
) -> TokenResponse:
    return controller.login(form.username, form.password)
