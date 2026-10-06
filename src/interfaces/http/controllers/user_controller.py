"""Controlador HTTP de usuarios y autenticación."""

from src.application.use_cases.user_use_cases import UserUseCases
from src.domain.entities.user import User, UserUpdate
from src.interfaces.http.schemas.user_schema import (
    TokenResponse,
    UserCreate,
    UserReplace,
    UserResponse,
)


def register(use_cases: UserUseCases, data: UserCreate) -> UserResponse:
    user = use_cases.register(
        data.name, str(data.email), data.password.get_secret_value()
    )
    return UserResponse.model_validate(user)


def login(use_cases: UserUseCases, email: str, password: str) -> TokenResponse:
    return TokenResponse.model_validate(use_cases.login(email, password))


def me(user: User) -> UserResponse:
    return UserResponse.model_validate(user)


def list_users(
    use_cases: UserUseCases, actor: User, offset: int, limit: int
) -> list[UserResponse]:
    return [
        UserResponse.model_validate(user)
        for user in use_cases.list(actor, offset, limit)
    ]


def get_user(use_cases: UserUseCases, actor: User, user_id: int) -> UserResponse:
    return UserResponse.model_validate(use_cases.get(actor, user_id))


def create_user(use_cases: UserUseCases, actor: User, data: UserCreate) -> UserResponse:
    user = use_cases.create(
        actor, data.name, str(data.email), data.password.get_secret_value()
    )
    return UserResponse.model_validate(user)


def update_user(
    use_cases: UserUseCases, actor: User, user_id: int, data: UserReplace
) -> UserResponse:
    updated = use_cases.update(
        actor,
        user_id,
        UserUpdate(
            name=data.name,
            email=str(data.email),
            is_active=data.is_active,
            password=data.password.get_secret_value()
            if data.password is not None
            else None,
        ),
    )
    return UserResponse.model_validate(updated)


def delete_user(use_cases: UserUseCases, actor: User, user_id: int) -> None:
    use_cases.delete(actor, user_id)
