"""Controlador HTTP de clases: convierte schemas y ejecuta casos de uso."""

import logging

from src.application.use_cases.gym_use_cases import GymUseCases
from src.domain.entities.gym import Clase
from src.interfaces.http.schemas.gym_schema import (
    ClaseInput,
    ClaseResponse,
    CupoClaseResponse,
)
from src.interfaces.http.schemas.list_query import ClaseQuery

logger = logging.getLogger(__name__)


def get_cupo(use_cases: GymUseCases, entity_id: int) -> CupoClaseResponse:
    return CupoClaseResponse.model_validate(use_cases.class_capacity(entity_id))


def list_clases(use_cases: GymUseCases, query: ClaseQuery) -> list[ClaseResponse]:
    entities = use_cases.list(Clase, query.offset, query.limit, query.to_filters())
    return [ClaseResponse.model_validate(entity) for entity in entities]


def get_clase(use_cases: GymUseCases, entity_id: int) -> ClaseResponse:
    entity = use_cases.get(Clase, entity_id)
    return ClaseResponse.model_validate(entity)


def create_clase(use_cases: GymUseCases, data: ClaseInput) -> ClaseResponse:
    entity = use_cases.create(Clase(**data.model_dump()))
    logger.info("Clase creada: id=%s nombre=%s", entity.id_clase, entity.nombre_clase)
    return ClaseResponse.model_validate(entity)


def update_clase(
    use_cases: GymUseCases, entity_id: int, data: ClaseInput
) -> ClaseResponse:
    entity = use_cases.update(Clase, entity_id, Clase(**data.model_dump()))
    return ClaseResponse.model_validate(entity)


def delete_clase(use_cases: GymUseCases, entity_id: int) -> None:
    use_cases.delete(Clase, entity_id)
    logger.info("Clase eliminada: id=%s", entity_id)
