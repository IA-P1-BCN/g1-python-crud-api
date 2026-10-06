"""Endpoints CRUD de clases."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response

from src.domain.repositories.gym_port import GymRepository
from src.interfaces.http.controllers import clase_controller as controller
from src.interfaces.http.dependencies import get_gym_repository
from src.interfaces.http.errors import CRUD_ERRORS
from src.interfaces.http.schemas.gym_schema import ClaseInput, ClaseResponse

router = APIRouter(prefix="/clases", tags=["clases"])
Repository = Annotated[GymRepository, Depends(get_gym_repository)]
EntityId = Annotated[int, Path(gt=0, le=2147483647)]


@router.get(
    "",
    response_model=list[ClaseResponse],
    summary="Lista clases",
    responses=CRUD_ERRORS,
)
def list_clases(
    repository: Repository,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[ClaseResponse]:
    return controller.list_clases(repository, offset, limit)


@router.get(
    "/{id_clase}",
    response_model=ClaseResponse,
    summary="Consulta clase por ID",
    responses=CRUD_ERRORS,
)
def get_clase(id_clase: EntityId, repository: Repository) -> ClaseResponse:
    return controller.get_clase(repository, id_clase)


@router.post(
    "",
    response_model=ClaseResponse,
    status_code=201,
    summary="Crea clase",
    responses=CRUD_ERRORS,
)
def create_clase(data: ClaseInput, repository: Repository) -> ClaseResponse:
    return controller.create_clase(repository, data)


@router.put(
    "/{id_clase}",
    response_model=ClaseResponse,
    summary="Sustituye los datos de clase",
    responses=CRUD_ERRORS,
)
def update_clase(
    id_clase: EntityId, data: ClaseInput, repository: Repository
) -> ClaseResponse:
    return controller.update_clase(repository, id_clase, data)


@router.delete(
    "/{id_clase}",
    response_model=None,
    response_class=Response,
    status_code=204,
    summary="Elimina clase",
    responses=CRUD_ERRORS,
)
def delete_clase(id_clase: EntityId, repository: Repository) -> Response:
    controller.delete_clase(repository, id_clase)
    return Response(status_code=204)
