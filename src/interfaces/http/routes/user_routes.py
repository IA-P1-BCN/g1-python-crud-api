"""CRUD de usuarios protegido por JWT y permisos de propietario/administrador."""

from typing import Annotated

from fastapi import APIRouter, Path, Query, Response

from src.interfaces.http.controllers import user_controller as controller
from src.interfaces.http.dependencies import CurrentUser, UseCases
from src.interfaces.http.errors import ERROR_RESPONSES
from src.interfaces.http.schemas.user_schema import (
    UserCreate,
    UserReplace,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["users"], responses=ERROR_RESPONSES)
UserId = Annotated[int, Path(gt=0, le=2147483647)]


@router.get(
    "/me", response_model=UserResponse, summary="Consulta el perfil autenticado"
)
def me(actor: CurrentUser) -> UserResponse:
    return controller.me(actor)


@router.get(
    "", response_model=list[UserResponse], summary="Lista usuarios como administrador"
)
def list_users(
    actor: CurrentUser,
    use_cases: UseCases,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[UserResponse]:
    return controller.list_users(use_cases, actor, offset, limit)


@router.get(
    "/{user_id}", response_model=UserResponse, summary="Consulta un usuario por ID"
)
def get_user(user_id: UserId, actor: CurrentUser, use_cases: UseCases) -> UserResponse:
    return controller.get_user(use_cases, actor, user_id)


@router.post(
    "",
    response_model=UserResponse,
    status_code=201,
    summary="Crea un usuario como administrador",
)
def create_user(
    data: UserCreate, actor: CurrentUser, use_cases: UseCases
) -> UserResponse:
    return controller.create_user(use_cases, actor, data)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualiza el perfil de un usuario",
)
def update_user(
    user_id: UserId, data: UserReplace, actor: CurrentUser, use_cases: UseCases
) -> UserResponse:
    return controller.update_user(use_cases, actor, user_id, data)


@router.delete(
    "/{user_id}",
    response_model=None,
    response_class=Response,
    status_code=204,
    summary="Elimina un usuario",
)
def delete_user(user_id: UserId, actor: CurrentUser, use_cases: UseCases) -> Response:
    controller.delete_user(use_cases, actor, user_id)
    return Response(status_code=204)
