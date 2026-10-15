"""Wiring HTTP: único punto de acceso del CRUD a infraestructura."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.application.use_cases.cuenta_use_cases import CuentaUseCases
from src.domain.repositories.cuenta_port import CuentaRepository
from src.domain.repositories.gym_port import GymRepository
from src.infrastructure.database.engine import get_session
from src.infrastructure.repositories.cuenta_repository import SqlAlchemyCuentaRepository
from src.infrastructure.repositories.gym_repository import SqlAlchemyGymRepository
from src.infrastructure.security.passwords import Argon2PasswordHasher
from src.interfaces.http.controllers.cuenta_controller import CuentaController


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
