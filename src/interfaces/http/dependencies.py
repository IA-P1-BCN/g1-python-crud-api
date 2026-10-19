"""Wiring HTTP: único punto de acceso del CRUD a infraestructura."""

from functools import lru_cache
from secrets import token_urlsafe
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from config.settings import get_settings
from src.application.use_cases.auth_use_cases import AuthUseCases
from src.application.use_cases.cuenta_use_cases import CuentaUseCases
from src.application.use_cases.gym_use_cases import GymUseCases
from src.domain.entities.cuenta import Cuenta
from src.domain.errors import ForbiddenError
from src.domain.repositories.cuenta_port import CuentaRepository
from src.domain.repositories.gym_port import GymRepository
from src.infrastructure.database.engine import get_session
from src.infrastructure.repositories.cuenta_repository import SqlAlchemyCuentaRepository
from src.infrastructure.repositories.gym_repository import SqlAlchemyGymRepository
from src.infrastructure.security.passwords import Argon2PasswordHasher
from src.infrastructure.security.tokens import JwtAccessTokens
from src.interfaces.http.controllers.auth_controller import AuthController
from src.interfaces.http.controllers.cuenta_controller import CuentaController
from src.interfaces.http.oauth import oauth2_scheme


def get_gym_repository(
    session: Annotated[Session, Depends(get_session)],
) -> GymRepository:
    return SqlAlchemyGymRepository(session)


def get_cuenta_repository(
    session: Annotated[Session, Depends(get_session)],
) -> CuentaRepository:
    return SqlAlchemyCuentaRepository(session)


def get_cuenta_use_cases(
    repository: Annotated[CuentaRepository, Depends(get_cuenta_repository)],
) -> CuentaUseCases:
    return CuentaUseCases(repository, Argon2PasswordHasher())


def get_cuenta_controller(
    use_cases: Annotated[CuentaUseCases, Depends(get_cuenta_use_cases)],
) -> CuentaController:
    return CuentaController(use_cases)


@lru_cache
def get_dummy_hash() -> str:
    return Argon2PasswordHasher().hash(token_urlsafe(32))


def get_access_tokens() -> JwtAccessTokens:
    settings = get_settings()
    return JwtAccessTokens(
        settings.secret_key.get_secret_value(), settings.access_token_expire_minutes
    )


def get_auth_controller(
    repository: Annotated[CuentaRepository, Depends(get_cuenta_repository)],
) -> AuthController:
    return AuthController(
        AuthUseCases(
            repository, Argon2PasswordHasher(), get_access_tokens(), get_dummy_hash()
        )
    )


def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    controller: Annotated[AuthController, Depends(get_auth_controller)],
) -> Cuenta:
    return controller.current_user(token)


def get_gym_use_cases(
    repository: Annotated[GymRepository, Depends(get_gym_repository)],
    cuenta: Annotated[Cuenta, Depends(get_current_user)],
) -> GymUseCases:
    return GymUseCases(repository, cuenta)


def requires_admin(
    cuenta: Annotated[Cuenta, Depends(get_current_user)],
) -> Cuenta:
    if cuenta.rol != "admin":
        raise ForbiddenError("Esta operación requiere rol admin")
    return cuenta


def requires_account_access(
    id: int,
    cuenta: Annotated[Cuenta, Depends(get_current_user)],
) -> Cuenta:
    if cuenta.rol != "admin" and cuenta.id != id:
        raise ForbiddenError("No puedes consultar una Cuenta ajena")
    return cuenta
