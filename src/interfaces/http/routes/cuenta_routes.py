"""Operaciones de Cuenta protegidas por JWT."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response

from src.domain.entities.cuenta import Cuenta
from src.interfaces.http.controllers.cuenta_controller import CuentaController
from src.interfaces.http.dependencies import get_cuenta_controller, get_current_user
from src.interfaces.http.errors import LIST_ERRORS, PROTECTED_ERRORS
from src.interfaces.http.schemas.cuenta_schema import (
    CuentaPatch,
    CuentaPut,
    CuentaResponse,
)
from src.interfaces.http.schemas.list_query import CuentaQuery

router = APIRouter(prefix="/users", tags=["cuentas"])
CurrentCuenta = Annotated[Cuenta, Depends(get_current_user)]
Controller = Annotated[CuentaController, Depends(get_cuenta_controller)]
CuentaId = Annotated[int, Path(gt=0, le=2147483647)]


@router.get(
    "/me",
    summary="Consultar mi Cuenta",
    response_model=CuentaResponse,
    responses=PROTECTED_ERRORS,
)
def me(cuenta: CurrentCuenta) -> CuentaResponse:
    return CuentaController.me(cuenta)


@router.get(
    "",
    summary="Listar Cuentas",
    response_model=list[CuentaResponse],
    responses={**PROTECTED_ERRORS, 400: LIST_ERRORS[400]},
)
def list_cuentas(
    query: Annotated[CuentaQuery, Query()],
    cuenta: CurrentCuenta,
    controller: Controller,
) -> list[CuentaResponse]:
    return controller.list(query)


@router.get(
    "/{id}",
    summary="Consultar una Cuenta",
    response_model=CuentaResponse,
    responses=PROTECTED_ERRORS,
)
def get_cuenta(
    id: CuentaId, cuenta: CurrentCuenta, controller: Controller
) -> CuentaResponse:
    return controller.get(id)


@router.put(
    "/{id}",
    summary="Sustituir los datos de una Cuenta",
    response_model=CuentaResponse,
    responses=PROTECTED_ERRORS,
)
def put_cuenta(
    id: CuentaId, data: CuentaPut, cuenta: CurrentCuenta, controller: Controller
) -> CuentaResponse:
    return controller.update(id, data)


@router.patch(
    "/{id}",
    summary="Editar parcialmente una Cuenta",
    response_model=CuentaResponse,
    responses=PROTECTED_ERRORS,
)
def patch_cuenta(
    id: CuentaId, data: CuentaPatch, cuenta: CurrentCuenta, controller: Controller
) -> CuentaResponse:
    return controller.update(id, data)


@router.delete(
    "/{id}",
    summary="Borrar una Cuenta",
    status_code=204,
    response_model=None,
    responses=PROTECTED_ERRORS,
)
def delete_cuenta(
    id: CuentaId, cuenta: CurrentCuenta, controller: Controller
) -> Response:
    controller.delete(id)
    return Response(status_code=204)
