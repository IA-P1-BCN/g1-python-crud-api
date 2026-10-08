"""Controlador HTTP de clases: convierte schemas y ejecuta casos de uso."""

import logging

from src.application.use_cases.gym_use_cases import GymUseCases
from src.domain.entities.gym import Clase
from src.domain.repositories.gym_port import GymRepository
from src.interfaces.http.schemas.gym_schema import ClaseInput, ClaseResponse

logger = logging.getLogger(__name__)


def list_clases(
    repository: GymRepository, offset: int, limit: int
) -> list[ClaseResponse]:
    entities = GymUseCases(repository).list(Clase, offset, limit)
    return [ClaseResponse.model_validate(entity) for entity in entities]


def get_clase(repository: GymRepository, entity_id: int) -> ClaseResponse:
    entity = GymUseCases(repository).get(Clase, entity_id)
    return ClaseResponse.model_validate(entity)


def create_clase(repository: GymRepository, data: ClaseInput) -> ClaseResponse:
    entity = GymUseCases(repository).create(Clase(**data.model_dump()))
    logger.info("Clase creada: id=%s nombre=%s", entity.id_clase, entity.nombre_clase)
    return ClaseResponse.model_validate(entity)


def update_clase(
    repository: GymRepository, entity_id: int, data: ClaseInput
) -> ClaseResponse:
    entity = GymUseCases(repository).update(
        Clase, entity_id, Clase(**data.model_dump())
    )
    return ClaseResponse.model_validate(entity)


def delete_clase(repository: GymRepository, entity_id: int) -> None:
    GymUseCases(repository).delete(Clase, entity_id)
    logger.info("Clase eliminada: id=%s", entity_id)
