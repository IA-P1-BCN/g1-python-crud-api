"""Wiring HTTP: único punto de acceso del CRUD a infraestructura."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.domain.repositories.gym_port import GymRepository
from src.infrastructure.database.engine import get_session
from src.infrastructure.repositories.gym_repository import SqlAlchemyGymRepository


def get_gym_repository(
    session: Annotated[Session, Depends(get_session)],
) -> GymRepository:
    return SqlAlchemyGymRepository(session)
