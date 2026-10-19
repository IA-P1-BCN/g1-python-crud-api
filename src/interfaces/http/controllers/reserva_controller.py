"""Controlador HTTP de reservas: convierte schemas y ejecuta casos de uso."""

import logging
from datetime import UTC, datetime

from src.application.use_cases.gym_use_cases import GymUseCases
from src.domain.entities.gym import IdentidadCliente, Reserva
from src.interfaces.http.schemas.gym_schema import ReservaInput, ReservaResponse
from src.interfaces.http.schemas.list_query import ReservaQuery

logger = logging.getLogger(__name__)


def _response(
    entity: Reserva, identidades: dict[int, IdentidadCliente]
) -> ReservaResponse:
    identidad = identidades.get(
        entity.id_cliente, IdentidadCliente(id_cliente=entity.id_cliente)
    )
    return ReservaResponse(
        id_reserva=entity.id_reserva,
        id_cliente=entity.id_cliente,
        id_clase=entity.id_clase,
        asistio=entity.asistio,
        fecha_reserva=entity.fecha_reserva,
        id_user=identidad.id_user,
        nombre=identidad.nombre,
        email=identidad.email,
    )


def _identidades(
    use_cases: GymUseCases, entities: list[Reserva]
) -> dict[int, IdentidadCliente]:
    return use_cases.identities_for_clientes(
        list({entity.id_cliente for entity in entities})
    )


def list_reservas(use_cases: GymUseCases, query: ReservaQuery) -> list[ReservaResponse]:
    entities = use_cases.list(Reserva, query.offset, query.limit, query.to_filters())
    identidades = _identidades(use_cases, entities)
    return [_response(entity, identidades) for entity in entities]


def get_reserva(use_cases: GymUseCases, entity_id: int) -> ReservaResponse:
    entity = use_cases.get(Reserva, entity_id)
    identidades = _identidades(use_cases, [entity])
    return _response(entity, identidades)


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
    identidades = _identidades(use_cases, [entity])
    return _response(entity, identidades)


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
    identidades = _identidades(use_cases, [entity])
    return _response(entity, identidades)


def delete_reserva(use_cases: GymUseCases, entity_id: int) -> None:
    use_cases.delete(Reserva, entity_id)
    logger.info("Reserva eliminada: id=%s", entity_id)
