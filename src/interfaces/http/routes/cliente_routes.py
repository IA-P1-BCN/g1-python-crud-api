"""Endpoints CRUD de clientes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response

from src.domain.repositories.gym_port import GymRepository
from src.interfaces.http.controllers import cliente_controller as controller
from src.interfaces.http.dependencies import get_gym_repository
from src.interfaces.http.errors import CRUD_ERRORS
from src.interfaces.http.schemas.gym_schema import ClienteInput, ClienteResponse

router = APIRouter(prefix="/clientes", tags=["clientes"])
Repository = Annotated[GymRepository, Depends(get_gym_repository)]
EntityId = Annotated[int, Path(gt=0, le=2147483647)]


@router.get(
    "",
    response_model=list[ClienteResponse],
    summary="Lista clientes",
    responses=CRUD_ERRORS,
)
def list_clientes(
    repository: Repository,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[ClienteResponse]:
    return controller.list_clientes(repository, offset, limit)


@router.get(
    "/{id_cliente}",
    response_model=ClienteResponse,
    summary="Consulta cliente por ID",
    responses=CRUD_ERRORS,
)
def get_cliente(id_cliente: EntityId, repository: Repository) -> ClienteResponse:
    return controller.get_cliente(repository, id_cliente)


@router.post(
    "",
    response_model=ClienteResponse,
    status_code=201,
    summary="Crea cliente",
    responses=CRUD_ERRORS,
)
def create_cliente(data: ClienteInput, repository: Repository) -> ClienteResponse:
    return controller.create_cliente(repository, data)


@router.put(
    "/{id_cliente}",
    response_model=ClienteResponse,
    summary="Sustituye los datos de cliente",
    responses=CRUD_ERRORS,
)
def update_cliente(
    id_cliente: EntityId, data: ClienteInput, repository: Repository
) -> ClienteResponse:
    return controller.update_cliente(repository, id_cliente, data)


@router.delete(
    "/{id_cliente}",
    response_model=None,
    response_class=Response,
    status_code=204,
    summary="Elimina cliente",
    responses=CRUD_ERRORS,
)
def delete_cliente(id_cliente: EntityId, repository: Repository) -> Response:
    controller.delete_cliente(repository, id_cliente)
    return Response(status_code=204)
