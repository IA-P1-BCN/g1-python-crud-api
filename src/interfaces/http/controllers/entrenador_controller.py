"""Controlador HTTP de entrenadores: convierte schemas y ejecuta casos de uso."""

from src.application.use_cases.gym_use_cases import GymUseCases
from src.domain.entities.gym import Entrenador
from src.domain.repositories.gym_port import GymRepository
from src.interfaces.http.schemas.gym_schema import EntrenadorInput, EntrenadorResponse


def list_entrenadores(
    repository: GymRepository, offset: int, limit: int
) -> list[EntrenadorResponse]:
    entities = GymUseCases(repository).list(Entrenador, offset, limit)
    return [EntrenadorResponse.model_validate(entity) for entity in entities]


def get_entrenador(repository: GymRepository, entity_id: int) -> EntrenadorResponse:
    entity = GymUseCases(repository).get(Entrenador, entity_id)
    return EntrenadorResponse.model_validate(entity)


def create_entrenador(
    repository: GymRepository, data: EntrenadorInput
) -> EntrenadorResponse:
    entity = GymUseCases(repository).create(Entrenador(**data.model_dump()))
    return EntrenadorResponse.model_validate(entity)


def update_entrenador(
    repository: GymRepository, entity_id: int, data: EntrenadorInput
) -> EntrenadorResponse:
    entity = GymUseCases(repository).update(
        Entrenador, entity_id, Entrenador(**data.model_dump())
    )
    return EntrenadorResponse.model_validate(entity)


def delete_entrenador(repository: GymRepository, entity_id: int) -> None:
    GymUseCases(repository).delete(Entrenador, entity_id)
