"""Controlador HTTP de clientes: convierte schemas y ejecuta casos de uso."""

import logging

from src.application.use_cases.gym_use_cases import GymUseCases
from src.domain.entities.gym import Cliente, IdentidadCliente
from src.interfaces.http.schemas.gym_schema import ClienteInput, ClienteResponse
from src.interfaces.http.schemas.list_query import ClienteQuery

logger = logging.getLogger(__name__)


def _response(
    entity: Cliente, identidades: dict[int, IdentidadCliente]
) -> ClienteResponse:
    identidad = identidades.get(
        entity.id_cliente, IdentidadCliente(id_cliente=entity.id_cliente)
    )
    return ClienteResponse(
        id_cliente=entity.id_cliente,
        estado_membresia=entity.estado_membresia,
        fecha_inscripcion=entity.fecha_inscripcion,
        id_user=identidad.id_user,
        nombre=identidad.nombre,
        email=identidad.email,
    )


def _identidades(
    use_cases: GymUseCases, entities: list[Cliente]
) -> dict[int, IdentidadCliente]:
    return use_cases.identities_for_clientes(
        [entity.id_cliente for entity in entities if entity.id_cliente is not None]
    )


def list_clientes(use_cases: GymUseCases, query: ClienteQuery) -> list[ClienteResponse]:
    entities = use_cases.list(Cliente, query.offset, query.limit, query.to_filters())
    identidades = _identidades(use_cases, entities)
    return [_response(entity, identidades) for entity in entities]


def get_cliente(use_cases: GymUseCases, entity_id: int) -> ClienteResponse:
    entity = use_cases.get(Cliente, entity_id)
    identidades = _identidades(use_cases, [entity])
    return _response(entity, identidades)


def create_cliente(use_cases: GymUseCases, data: ClienteInput) -> ClienteResponse:
    entity = use_cases.create(Cliente(**data.model_dump()))
    logger.info("Cliente creado: id=%s", entity.id_cliente)
    identidades = _identidades(use_cases, [entity])
    return _response(entity, identidades)


def update_cliente(
    use_cases: GymUseCases, entity_id: int, data: ClienteInput
) -> ClienteResponse:
    entity = use_cases.update(Cliente, entity_id, Cliente(**data.model_dump()))
    identidades = _identidades(use_cases, [entity])
    return _response(entity, identidades)


def delete_cliente(use_cases: GymUseCases, entity_id: int) -> None:
    use_cases.delete(Cliente, entity_id)
    logger.info("Cliente eliminado: id=%s", entity_id)
