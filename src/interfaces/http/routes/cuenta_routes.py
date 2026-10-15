"""Operaciones de Cuenta protegidas por JWT."""

from typing import Annotated

from fastapi import APIRouter, Depends

from src.domain.entities.cuenta import Cuenta
from src.interfaces.http.controllers.cuenta_controller import CuentaController
from src.interfaces.http.dependencies import get_current_user
from src.interfaces.http.errors import PROTECTED_ERRORS
from src.interfaces.http.schemas.cuenta_schema import CuentaResponse

router = APIRouter(prefix="/users", tags=["cuentas"])
CurrentCuenta = Annotated[Cuenta, Depends(get_current_user)]


@router.get(
    "/me",
    summary="Consultar mi Cuenta",
    response_model=CuentaResponse,
    responses=PROTECTED_ERRORS,
)
def me(cuenta: CurrentCuenta) -> CuentaResponse:
    return CuentaController.me(cuenta)
