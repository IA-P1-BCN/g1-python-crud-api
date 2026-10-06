"""Endpoints CRUD de pagos."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response

from src.domain.repositories.gym_port import GymRepository
from src.interfaces.http.controllers import pago_controller as controller
from src.interfaces.http.dependencies import get_gym_repository
from src.interfaces.http.errors import CRUD_ERRORS
from src.interfaces.http.schemas.gym_schema import PagoInput, PagoResponse

router = APIRouter(prefix="/pagos", tags=["pagos"])
Repository = Annotated[GymRepository, Depends(get_gym_repository)]
EntityId = Annotated[int, Path(gt=0, le=2147483647)]


@router.get(
    "", response_model=list[PagoResponse], summary="Lista pagos", responses=CRUD_ERRORS
)
def list_pagos(
    repository: Repository,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[PagoResponse]:
    return controller.list_pagos(repository, offset, limit)


@router.get(
    "/{id_pago}",
    response_model=PagoResponse,
    summary="Consulta pago por ID",
    responses=CRUD_ERRORS,
)
def get_pago(id_pago: EntityId, repository: Repository) -> PagoResponse:
    return controller.get_pago(repository, id_pago)


@router.post(
    "",
    response_model=PagoResponse,
    status_code=201,
    summary="Crea pago",
    responses=CRUD_ERRORS,
)
def create_pago(data: PagoInput, repository: Repository) -> PagoResponse:
    return controller.create_pago(repository, data)


@router.put(
    "/{id_pago}",
    response_model=PagoResponse,
    summary="Sustituye los datos de pago",
    responses=CRUD_ERRORS,
)
def update_pago(
    id_pago: EntityId, data: PagoInput, repository: Repository
) -> PagoResponse:
    return controller.update_pago(repository, id_pago, data)


@router.delete(
    "/{id_pago}",
    response_model=None,
    response_class=Response,
    status_code=204,
    summary="Elimina pago",
    responses=CRUD_ERRORS,
)
def delete_pago(id_pago: EntityId, repository: Repository) -> Response:
    controller.delete_pago(repository, id_pago)
    return Response(status_code=204)
