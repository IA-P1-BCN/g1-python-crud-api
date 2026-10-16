"""Wiring HTTP: único punto de acceso del CRUD a infraestructura."""

from functools import lru_cache
from secrets import token_urlsafe
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from config.settings import get_settings
from src.application.use_cases.auth_use_cases import AuthUseCases
from src.application.use_cases.cuenta_use_cases import CuentaUseCases
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


def get_cuenta_controller(
    repository: Annotated[CuentaRepository, Depends(get_cuenta_repository)],
) -> CuentaController:
    return CuentaController(CuentaUseCases(repository, Argon2PasswordHasher()))


@lru_cache
def get_dummy_hash() -> str:
    return Argon2PasswordHasher().hash(token_urlsafe(32))


def get_access_tokens() -> JwtAccessTokens:
    return JwtAccessTokens(get_settings().secret_key.get_secret_value())


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


def requires_admin(
    cuenta: Annotated[Cuenta, Depends(get_current_user)],
) -> Cuenta:
    if cuenta.rol != "admin":
        raise ForbiddenError("Esta operación requiere rol admin")
    return cuenta
