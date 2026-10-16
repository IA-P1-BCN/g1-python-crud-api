"""Controlador HTTP de reservas: convierte schemas y ejecuta casos de uso."""

import logging
from datetime import UTC, datetime

from src.application.use_cases.gym_use_cases import GymUseCases
from src.domain.entities.gym import Reserva
from src.interfaces.http.schemas.gym_schema import ReservaInput, ReservaResponse
from src.interfaces.http.schemas.list_query import ReservaQuery

logger = logging.getLogger(__name__)


def list_reservas(use_cases: GymUseCases, query: ReservaQuery) -> list[ReservaResponse]:
    entities = use_cases.list(Reserva, query.offset, query.limit, query.to_filters())
    return [ReservaResponse.model_validate(entity) for entity in entities]


def get_reserva(use_cases: GymUseCases, entity_id: int) -> ReservaResponse:
    entity = use_cases.get(Reserva, entity_id)
    return ReservaResponse.model_validate(entity)


def create_reserva(use_cases: GymUseCases, data: ReservaInput) -> ReservaResponse:
    entity = use_cases.create(
        Reserva(
            **data.model_dump(), fecha_reserva=datetime.now(UTC).replace(tzinfo=None)
        )
    )
    logger.info(
        "Reserva creada: id=%s cliente_id=%s clase_id=%s",
        entity.id_reserva,
        entity.id_cliente,
        entity.id_clase,
    )
    return ReservaResponse.model_validate(entity)


def update_reserva(
    use_cases: GymUseCases, entity_id: int, data: ReservaInput
) -> ReservaResponse:
    entity = use_cases.update(
        Reserva,
        entity_id,
        Reserva(
            **data.model_dump(), fecha_reserva=datetime.now(UTC).replace(tzinfo=None)
        ),
    )
    return ReservaResponse.model_validate(entity)


def delete_reserva(use_cases: GymUseCases, entity_id: int) -> None:
    use_cases.delete(Reserva, entity_id)
    logger.info("Reserva eliminada: id=%s", entity_id)
