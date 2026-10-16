"""Operaciones de Cuenta protegidas por JWT."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response

from src.domain.entities.cuenta import Cuenta
from src.interfaces.http.controllers.cuenta_controller import CuentaController
from src.interfaces.http.dependencies import (
    get_cuenta_controller,
    get_current_user,
    requires_account_access,
    requires_admin,
)
from src.interfaces.http.errors import LIST_ERRORS, PROTECTED_ERRORS
from src.interfaces.http.schemas.cuenta_schema import (
    CuentaEntrenadorInput,
    CuentaPatch,
    CuentaPut,
    CuentaResponse,
    CuentaSelfPatch,
)
from src.interfaces.http.schemas.list_query import CuentaQuery

router = APIRouter(prefix="/users", tags=["cuentas"])
CurrentCuenta = Annotated[Cuenta, Depends(get_current_user)]
AdminCuenta = Annotated[Cuenta, Depends(requires_admin)]
AccessibleCuenta = Annotated[Cuenta, Depends(requires_account_access)]
Controller = Annotated[CuentaController, Depends(get_cuenta_controller)]
CuentaId = Annotated[int, Path(gt=0, le=2147483647)]


@router.get(
    "/me",
    summary="Consultar mi Cuenta",
    description="Resuelve la Cuenta del JWT y comprueba su estado actual; nunca devuelve credenciales.",
    response_model=CuentaResponse,
    responses=PROTECTED_ERRORS,
)
def me(cuenta: CurrentCuenta) -> CuentaResponse:
    return CuentaController.me(cuenta)


@router.patch(
    "/me",
    summary="Editar mi Cuenta",
    description="Nombre/email propios; cambiar password exige current_password correcta (403 si no coincide). No permite rol, activo ni vínculos. Los cambios se confirman juntos.",
    response_model=CuentaResponse,
    responses=PROTECTED_ERRORS,
)
def patch_me(
    data: CuentaSelfPatch, cuenta: CurrentCuenta, controller: Controller
) -> CuentaResponse:
    return controller.update_self(cuenta.id, data)


@router.get(
    "",
    summary="Listar Cuentas",
    description="Solo admin activo. Filtros combinados antes de paginar, orden por id y máximo 100 resultados. Rangos UTC inclusivos sin zona.",
    response_model=list[CuentaResponse],
    responses={**PROTECTED_ERRORS, 400: LIST_ERRORS[400]},
)
def list_cuentas(
    query: Annotated[CuentaQuery, Query()],
    cuenta: AdminCuenta,
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
    id: CuentaId, cuenta: AccessibleCuenta, controller: Controller
) -> CuentaResponse:
    return controller.get(id)


@router.put(
    "/{id}",
    summary="Sustituir los datos de una Cuenta",
    description="Solo admin. Exige nombre y email. Password es opcional y conserva el hash si se omite; si se envía, se sustituye con hash. No permite rol, activo ni id_cliente.",
    response_model=CuentaResponse,
    responses=PROTECTED_ERRORS,
)
def put_cuenta(
    id: CuentaId, data: CuentaPut, cuenta: AdminCuenta, controller: Controller
) -> CuentaResponse:
    return controller.update(id, data)


@router.patch(
    "/{id}",
    summary="Editar parcialmente una Cuenta",
    description="Solo admin. Acepta nombre, email y password; conserva campos omitidos. Null explícito, campos protegidos o cuerpo vacío producen 422. La edición propia usa PATCH /users/me.",
    response_model=CuentaResponse,
    responses=PROTECTED_ERRORS,
)
def patch_cuenta(
    id: CuentaId, data: CuentaPatch, cuenta: AdminCuenta, controller: Controller
) -> CuentaResponse:
    return controller.update(id, data)


@router.delete(
    "/{id}",
    summary="Borrar una Cuenta",
    description="Solo admin activo. Borrado físico: conserva Cliente e historial del gimnasio. Los tokens de la Cuenta eliminada dejan de resolver identidad.",
    status_code=204,
    response_model=None,
    responses=PROTECTED_ERRORS,
)
def delete_cuenta(
    id: CuentaId, cuenta: AdminCuenta, controller: Controller
) -> Response:
    controller.delete(id)
    return Response(status_code=204)


@router.put(
    "/{id}/entrenador",
    summary="Vincular una Cuenta staff con su Entrenador",
    description="Solo admin. Envía id_entrenador positivo o null para desvincular. El vínculo es único; no se deduce por nombre o email.",
    response_model=CuentaResponse,
    responses=PROTECTED_ERRORS,
)
def set_entrenador(
    id: CuentaId,
    data: CuentaEntrenadorInput,
    cuenta: AdminCuenta,
    controller: Controller,
) -> CuentaResponse:
    return controller.set_entrenador(id, data.id_entrenador)
