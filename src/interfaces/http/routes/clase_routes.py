"""Endpoints CRUD de clases."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response

from src.application.use_cases.gym_use_cases import GymUseCases
from src.interfaces.http.controllers import clase_controller as controller
from src.interfaces.http.dependencies import get_gym_use_cases
from src.interfaces.http.errors import CRUD_ERRORS, LIST_ERRORS
from src.interfaces.http.schemas.gym_schema import (
    ClaseInput,
    ClaseResponse,
    CupoClaseResponse,
)
from src.interfaces.http.schemas.list_query import ClaseQuery

router = APIRouter(prefix="/clases", tags=["clases"])
UseCases = Annotated[GymUseCases, Depends(get_gym_use_cases)]
EntityId = Annotated[int, Path(gt=0, le=2147483647)]


@router.get(
    "/{id_clase}/cupo",
    response_model=CupoClaseResponse,
    summary="Consulta el cupo agregado de una clase",
    description="Cuenta reservas sin devolver datos de clientes. Staff solo consulta sus clases.",
    responses=CRUD_ERRORS,
)
def get_cupo(id_clase: EntityId, use_cases: UseCases) -> CupoClaseResponse:
    return controller.get_cupo(use_cases, id_clase)


@router.get(
    "",
    response_model=list[ClaseResponse],
    summary="Lista clases",
    responses=LIST_ERRORS,
)
def list_clases(
    use_cases: UseCases,
    query: Annotated[ClaseQuery, Query()],
) -> list[ClaseResponse]:
    return controller.list_clases(use_cases, query)


@router.get(
    "/{id_clase}",
    response_model=ClaseResponse,
    summary="Consulta clase por ID",
    responses=CRUD_ERRORS,
)
def get_clase(id_clase: EntityId, use_cases: UseCases) -> ClaseResponse:
    return controller.get_clase(use_cases, id_clase)


@router.post(
    "",
    response_model=ClaseResponse,
    status_code=201,
    summary="Crea clase",
    responses=CRUD_ERRORS,
)
def create_clase(data: ClaseInput, use_cases: UseCases) -> ClaseResponse:
    return controller.create_clase(use_cases, data)


@router.put(
    "/{id_clase}",
    response_model=ClaseResponse,
    summary="Sustituye los datos de clase",
    responses=CRUD_ERRORS,
)
def update_clase(
    id_clase: EntityId, data: ClaseInput, use_cases: UseCases
) -> ClaseResponse:
    return controller.update_clase(use_cases, id_clase, data)


@router.delete(
    "/{id_clase}",
    response_model=None,
    response_class=Response,
    status_code=204,
    summary="Elimina clase",
    responses=CRUD_ERRORS,
)
def delete_clase(id_clase: EntityId, use_cases: UseCases) -> Response:
    controller.delete_clase(use_cases, id_clase)
    return Response(status_code=204)
