"""Registro y autenticación públicos de Cuentas."""

from typing import Annotated

from fastapi import APIRouter, Depends

from src.interfaces.http.controllers.cuenta_controller import CuentaController
from src.interfaces.http.dependencies import get_cuenta_controller
from src.interfaces.http.errors import CRUD_ERRORS
from src.interfaces.http.schemas.cuenta_schema import CuentaRegister, CuentaResponse

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
