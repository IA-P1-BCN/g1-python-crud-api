"""Registro y autenticación públicos de Cuentas."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.interfaces.http.controllers.auth_controller import AuthController
from src.interfaces.http.controllers.cuenta_controller import CuentaController
from src.interfaces.http.dependencies import get_auth_controller, get_cuenta_controller
from src.interfaces.http.errors import CRUD_ERRORS, LOGIN_ERRORS
from src.interfaces.http.schemas.auth_schema import TokenResponse
from src.interfaces.http.schemas.cuenta_schema import CuentaRegister, CuentaResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    summary="Registrar una Cuenta",
    description="Registro público. Crea rol cliente; crear_cliente=true añade un Cliente Inactivo nuevo. No vincula Clientes preexistentes por email.",
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
    description="OAuth2 Password Flow público: username es el email. Devuelve un JWT Bearer de 30 minutos. Usa Authorize en Swagger con las mismas credenciales.",
    response_model=TokenResponse,
    responses=LOGIN_ERRORS,
)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    controller: Annotated[AuthController, Depends(get_auth_controller)],
) -> TokenResponse:
    return controller.login(form.username, form.password)
