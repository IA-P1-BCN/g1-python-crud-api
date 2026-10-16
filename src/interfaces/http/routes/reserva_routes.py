"""Endpoints CRUD de reservas."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response

from src.application.use_cases.gym_use_cases import GymUseCases
from src.interfaces.http.controllers import reserva_controller as controller
from src.interfaces.http.dependencies import get_gym_use_cases
from src.interfaces.http.errors import CRUD_ERRORS, LIST_ERRORS
from src.interfaces.http.schemas.gym_schema import ReservaInput, ReservaResponse
from src.interfaces.http.schemas.list_query import ReservaQuery

router = APIRouter(prefix="/reservas", tags=["reservas"])
UseCases = Annotated[GymUseCases, Depends(get_gym_use_cases)]
EntityId = Annotated[int, Path(gt=0, le=2147483647)]


@router.get(
    "",
    response_model=list[ReservaResponse],
    summary="Lista reservas",
    responses=LIST_ERRORS,
)
def list_reservas(
    use_cases: UseCases,
    query: Annotated[ReservaQuery, Query()],
) -> list[ReservaResponse]:
    return controller.list_reservas(use_cases, query)


@router.get(
    "/{id_reserva}",
    response_model=ReservaResponse,
    summary="Consulta reserva por ID",
    responses=CRUD_ERRORS,
)
def get_reserva(id_reserva: EntityId, use_cases: UseCases) -> ReservaResponse:
    return controller.get_reserva(use_cases, id_reserva)


@router.post(
    "",
    response_model=ReservaResponse,
    status_code=201,
    summary="Crea reserva",
    responses=CRUD_ERRORS,
)
def create_reserva(data: ReservaInput, use_cases: UseCases) -> ReservaResponse:
    return controller.create_reserva(use_cases, data)


@router.put(
    "/{id_reserva}",
    response_model=ReservaResponse,
    summary="Sustituye los datos de reserva",
    responses=CRUD_ERRORS,
)
def update_reserva(
    id_reserva: EntityId, data: ReservaInput, use_cases: UseCases
) -> ReservaResponse:
    return controller.update_reserva(use_cases, id_reserva, data)


@router.delete(
    "/{id_reserva}",
    response_model=None,
    response_class=Response,
    status_code=204,
    summary="Elimina reserva",
    responses=CRUD_ERRORS,
)
def delete_reserva(id_reserva: EntityId, use_cases: UseCases) -> Response:
    controller.delete_reserva(use_cases, id_reserva)
    return Response(status_code=204)
