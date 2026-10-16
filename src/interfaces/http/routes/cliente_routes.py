"""Endpoints CRUD de clientes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response

from src.application.use_cases.gym_use_cases import GymUseCases
from src.interfaces.http.controllers import cliente_controller as controller
from src.interfaces.http.dependencies import get_gym_use_cases
from src.interfaces.http.errors import CRUD_ERRORS, LIST_ERRORS
from src.interfaces.http.schemas.gym_schema import ClienteInput, ClienteResponse
from src.interfaces.http.schemas.list_query import ClienteQuery

router = APIRouter(prefix="/clientes", tags=["clientes"])
UseCases = Annotated[GymUseCases, Depends(get_gym_use_cases)]
EntityId = Annotated[int, Path(gt=0, le=2147483647)]


@router.get(
    "",
    response_model=list[ClienteResponse],
    summary="Lista clientes",
    responses=LIST_ERRORS,
)
def list_clientes(
    use_cases: UseCases,
    query: Annotated[ClienteQuery, Query()],
) -> list[ClienteResponse]:
    return controller.list_clientes(use_cases, query)


@router.get(
    "/{id_cliente}",
    response_model=ClienteResponse,
    summary="Consulta cliente por ID",
    responses=CRUD_ERRORS,
)
def get_cliente(id_cliente: EntityId, use_cases: UseCases) -> ClienteResponse:
    return controller.get_cliente(use_cases, id_cliente)


@router.post(
    "",
    response_model=ClienteResponse,
    status_code=201,
    summary="Crea cliente",
    responses=CRUD_ERRORS,
)
def create_cliente(data: ClienteInput, use_cases: UseCases) -> ClienteResponse:
    return controller.create_cliente(use_cases, data)


@router.put(
    "/{id_cliente}",
    response_model=ClienteResponse,
    summary="Sustituye los datos de cliente",
    responses=CRUD_ERRORS,
)
def update_cliente(
    id_cliente: EntityId, data: ClienteInput, use_cases: UseCases
) -> ClienteResponse:
    return controller.update_cliente(use_cases, id_cliente, data)


@router.delete(
    "/{id_cliente}",
    response_model=None,
    response_class=Response,
    status_code=204,
    summary="Elimina cliente",
    responses=CRUD_ERRORS,
)
def delete_cliente(id_cliente: EntityId, use_cases: UseCases) -> Response:
    controller.delete_cliente(use_cases, id_cliente)
    return Response(status_code=204)
