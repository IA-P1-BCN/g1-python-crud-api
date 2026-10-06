"""Endpoints CRUD de reservas."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response

from src.domain.repositories.gym_port import GymRepository
from src.interfaces.http.controllers import reserva_controller as controller
from src.interfaces.http.dependencies import get_gym_repository
from src.interfaces.http.errors import CRUD_ERRORS
from src.interfaces.http.schemas.gym_schema import ReservaInput, ReservaResponse

router = APIRouter(prefix="/reservas", tags=["reservas"])
Repository = Annotated[GymRepository, Depends(get_gym_repository)]
EntityId = Annotated[int, Path(gt=0, le=2147483647)]


@router.get(
    "",
    response_model=list[ReservaResponse],
    summary="Lista reservas",
    responses=CRUD_ERRORS,
)
def list_reservas(
    repository: Repository,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[ReservaResponse]:
    return controller.list_reservas(repository, offset, limit)


@router.get(
    "/{id_reserva}",
    response_model=ReservaResponse,
    summary="Consulta reserva por ID",
    responses=CRUD_ERRORS,
)
def get_reserva(id_reserva: EntityId, repository: Repository) -> ReservaResponse:
    return controller.get_reserva(repository, id_reserva)


@router.post(
    "",
    response_model=ReservaResponse,
    status_code=201,
    summary="Crea reserva",
    responses=CRUD_ERRORS,
)
def create_reserva(data: ReservaInput, repository: Repository) -> ReservaResponse:
    return controller.create_reserva(repository, data)


@router.put(
    "/{id_reserva}",
    response_model=ReservaResponse,
    summary="Sustituye los datos de reserva",
    responses=CRUD_ERRORS,
)
def update_reserva(
    id_reserva: EntityId, data: ReservaInput, repository: Repository
) -> ReservaResponse:
    return controller.update_reserva(repository, id_reserva, data)


@router.delete(
    "/{id_reserva}",
    response_model=None,
    response_class=Response,
    status_code=204,
    summary="Elimina reserva",
    responses=CRUD_ERRORS,
)
def delete_reserva(id_reserva: EntityId, repository: Repository) -> Response:
    controller.delete_reserva(repository, id_reserva)
    return Response(status_code=204)
