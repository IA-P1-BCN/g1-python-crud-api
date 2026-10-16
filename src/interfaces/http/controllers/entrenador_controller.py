"""Controlador HTTP de entrenadores: convierte schemas y ejecuta casos de uso."""

import logging

from src.application.use_cases.gym_use_cases import GymUseCases
from src.domain.entities.gym import Entrenador
from src.interfaces.http.schemas.gym_schema import EntrenadorInput, EntrenadorResponse
from src.interfaces.http.schemas.list_query import EntrenadorQuery

logger = logging.getLogger(__name__)


def list_entrenadores(
    use_cases: GymUseCases, query: EntrenadorQuery
) -> list[EntrenadorResponse]:
    entities = use_cases.list(Entrenador, query.offset, query.limit, query.to_filters())
    return [EntrenadorResponse.model_validate(entity) for entity in entities]


def get_entrenador(use_cases: GymUseCases, entity_id: int) -> EntrenadorResponse:
    entity = use_cases.get(Entrenador, entity_id)
    return EntrenadorResponse.model_validate(entity)


def create_entrenador(
    use_cases: GymUseCases, data: EntrenadorInput
) -> EntrenadorResponse:
    entity = use_cases.create(Entrenador(**data.model_dump()))
    logger.info(
        "Entrenador creado: id=%s nombre=%s", entity.id_entrenador, entity.nombre
    )
    return EntrenadorResponse.model_validate(entity)


def update_entrenador(
    use_cases: GymUseCases, entity_id: int, data: EntrenadorInput
) -> EntrenadorResponse:
    entity = use_cases.update(Entrenador, entity_id, Entrenador(**data.model_dump()))
    return EntrenadorResponse.model_validate(entity)


def delete_entrenador(use_cases: GymUseCases, entity_id: int) -> None:
    use_cases.delete(Entrenador, entity_id)
    logger.info("Entrenador eliminado: id=%s", entity_id)
