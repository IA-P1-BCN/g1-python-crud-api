"""Endpoints CRUD de pagos."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response

from src.application.use_cases.gym_use_cases import GymUseCases
from src.interfaces.http.controllers import pago_controller as controller
from src.interfaces.http.dependencies import get_gym_use_cases
from src.interfaces.http.errors import CRUD_ERRORS, LIST_ERRORS
from src.interfaces.http.schemas.gym_schema import PagoInput, PagoResponse
from src.interfaces.http.schemas.list_query import PagoQuery

router = APIRouter(prefix="/pagos", tags=["pagos"])
UseCases = Annotated[GymUseCases, Depends(get_gym_use_cases)]
EntityId = Annotated[int, Path(gt=0, le=2147483647)]


@router.get(
    "", response_model=list[PagoResponse], summary="Lista pagos", responses=LIST_ERRORS
)
def list_pagos(
    use_cases: UseCases,
    query: Annotated[PagoQuery, Query()],
) -> list[PagoResponse]:
    return controller.list_pagos(use_cases, query)


@router.get(
    "/{id_pago}",
    response_model=PagoResponse,
    summary="Consulta pago por ID",
    responses=CRUD_ERRORS,
)
def get_pago(id_pago: EntityId, use_cases: UseCases) -> PagoResponse:
    return controller.get_pago(use_cases, id_pago)


@router.post(
    "",
    response_model=PagoResponse,
    status_code=201,
    summary="Crea pago",
    responses=CRUD_ERRORS,
)
def create_pago(data: PagoInput, use_cases: UseCases) -> PagoResponse:
    return controller.create_pago(use_cases, data)


@router.put(
    "/{id_pago}",
    response_model=PagoResponse,
    summary="Sustituye los datos de pago",
    responses=CRUD_ERRORS,
)
def update_pago(
    id_pago: EntityId, data: PagoInput, use_cases: UseCases
) -> PagoResponse:
    return controller.update_pago(use_cases, id_pago, data)


@router.delete(
    "/{id_pago}",
    response_model=None,
    response_class=Response,
    status_code=204,
    summary="Elimina pago",
    responses=CRUD_ERRORS,
)
def delete_pago(id_pago: EntityId, use_cases: UseCases) -> Response:
    controller.delete_pago(use_cases, id_pago)
    return Response(status_code=204)
