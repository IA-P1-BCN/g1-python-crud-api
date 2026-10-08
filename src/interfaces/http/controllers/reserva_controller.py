"""Controlador HTTP de reservas: convierte schemas y ejecuta casos de uso."""

import logging
from datetime import UTC, datetime

from src.application.use_cases.gym_use_cases import GymUseCases
from src.domain.entities.gym import Reserva
from src.domain.repositories.gym_port import GymRepository
from src.interfaces.http.schemas.gym_schema import ReservaInput, ReservaResponse

logger = logging.getLogger(__name__)


def list_reservas(
    repository: GymRepository, offset: int, limit: int
) -> list[ReservaResponse]:
    entities = GymUseCases(repository).list(Reserva, offset, limit)
    return [ReservaResponse.model_validate(entity) for entity in entities]


def get_reserva(repository: GymRepository, entity_id: int) -> ReservaResponse:
    entity = GymUseCases(repository).get(Reserva, entity_id)
    return ReservaResponse.model_validate(entity)


def create_reserva(repository: GymRepository, data: ReservaInput) -> ReservaResponse:
    entity = GymUseCases(repository).create(
        Reserva(
            **data.model_dump(), fecha_reserva=datetime.now(UTC).replace(tzinfo=None)
        )
    )
    logger.info("Reserva creada: id=%s cliente_id=%s clase_id=%s", entity.id_reserva, entity.id_cliente, entity.id_clase)
    return ReservaResponse.model_validate(entity)


def update_reserva(
    repository: GymRepository, entity_id: int, data: ReservaInput
) -> ReservaResponse:
    entity = GymUseCases(repository).update(
        Reserva,
        entity_id,
        Reserva(
            **data.model_dump(), fecha_reserva=datetime.now(UTC).replace(tzinfo=None)
        ),
    )
    return ReservaResponse.model_validate(entity)


def delete_reserva(repository: GymRepository, entity_id: int) -> None:
    GymUseCases(repository).delete(Reserva, entity_id)
    logger.info("Reserva eliminada: id=%s", entity_id)
