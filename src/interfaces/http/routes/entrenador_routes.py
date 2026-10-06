"""Endpoints CRUD de entrenadores."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response

from src.domain.repositories.gym_port import GymRepository
from src.interfaces.http.controllers import entrenador_controller as controller
from src.interfaces.http.dependencies import get_gym_repository
from src.interfaces.http.errors import CRUD_ERRORS
from src.interfaces.http.schemas.gym_schema import EntrenadorInput, EntrenadorResponse

router = APIRouter(prefix="/entrenadores", tags=["entrenadores"])
Repository = Annotated[GymRepository, Depends(get_gym_repository)]
EntityId = Annotated[int, Path(gt=0, le=2147483647)]


@router.get(
    "",
    response_model=list[EntrenadorResponse],
    summary="Lista entrenadores",
    responses=CRUD_ERRORS,
)
def list_entrenadores(
    repository: Repository,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[EntrenadorResponse]:
    return controller.list_entrenadores(repository, offset, limit)


@router.get(
    "/{id_entrenador}",
    response_model=EntrenadorResponse,
    summary="Consulta entrenador por ID",
    responses=CRUD_ERRORS,
)
def get_entrenador(
    id_entrenador: EntityId, repository: Repository
) -> EntrenadorResponse:
    return controller.get_entrenador(repository, id_entrenador)


@router.post(
    "",
    response_model=EntrenadorResponse,
    status_code=201,
    summary="Crea entrenador",
    responses=CRUD_ERRORS,
)
def create_entrenador(
    data: EntrenadorInput, repository: Repository
) -> EntrenadorResponse:
    return controller.create_entrenador(repository, data)


@router.put(
    "/{id_entrenador}",
    response_model=EntrenadorResponse,
    summary="Sustituye los datos de entrenador",
    responses=CRUD_ERRORS,
)
def update_entrenador(
    id_entrenador: EntityId, data: EntrenadorInput, repository: Repository
) -> EntrenadorResponse:
    return controller.update_entrenador(repository, id_entrenador, data)


@router.delete(
    "/{id_entrenador}",
    response_model=None,
    response_class=Response,
    status_code=204,
    summary="Elimina entrenador",
    responses=CRUD_ERRORS,
)
def delete_entrenador(id_entrenador: EntityId, repository: Repository) -> Response:
    controller.delete_entrenador(repository, id_entrenador)
    return Response(status_code=204)
