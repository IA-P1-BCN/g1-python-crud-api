"""Endpoints CRUD de entrenadores."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response

from src.application.use_cases.gym_use_cases import GymUseCases
from src.interfaces.http.controllers import entrenador_controller as controller
from src.interfaces.http.dependencies import get_gym_use_cases
from src.interfaces.http.errors import CRUD_ERRORS, LIST_ERRORS
from src.interfaces.http.schemas.gym_schema import EntrenadorInput, EntrenadorResponse
from src.interfaces.http.schemas.list_query import EntrenadorQuery

router = APIRouter(prefix="/entrenadores", tags=["entrenadores"])
UseCases = Annotated[GymUseCases, Depends(get_gym_use_cases)]
EntityId = Annotated[int, Path(gt=0, le=2147483647)]


@router.get(
    "",
    response_model=list[EntrenadorResponse],
    summary="Lista entrenadores",
    responses=LIST_ERRORS,
)
def list_entrenadores(
    use_cases: UseCases,
    query: Annotated[EntrenadorQuery, Query()],
) -> list[EntrenadorResponse]:
    return controller.list_entrenadores(use_cases, query)


@router.get(
    "/{id_entrenador}",
    response_model=EntrenadorResponse,
    summary="Consulta entrenador por ID",
    responses=CRUD_ERRORS,
)
def get_entrenador(id_entrenador: EntityId, use_cases: UseCases) -> EntrenadorResponse:
    return controller.get_entrenador(use_cases, id_entrenador)


@router.post(
    "",
    response_model=EntrenadorResponse,
    status_code=201,
    summary="Crea entrenador",
    responses=CRUD_ERRORS,
)
def create_entrenador(data: EntrenadorInput, use_cases: UseCases) -> EntrenadorResponse:
    return controller.create_entrenador(use_cases, data)


@router.put(
    "/{id_entrenador}",
    response_model=EntrenadorResponse,
    summary="Sustituye los datos de entrenador",
    responses=CRUD_ERRORS,
)
def update_entrenador(
    id_entrenador: EntityId, data: EntrenadorInput, use_cases: UseCases
) -> EntrenadorResponse:
    return controller.update_entrenador(use_cases, id_entrenador, data)


@router.delete(
    "/{id_entrenador}",
    response_model=None,
    response_class=Response,
    status_code=204,
    summary="Elimina entrenador",
    responses=CRUD_ERRORS,
)
def delete_entrenador(id_entrenador: EntityId, use_cases: UseCases) -> Response:
    controller.delete_entrenador(use_cases, id_entrenador)
    return Response(status_code=204)
