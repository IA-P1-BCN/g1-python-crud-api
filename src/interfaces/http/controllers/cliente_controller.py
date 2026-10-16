"""Controlador HTTP de clientes: convierte schemas y ejecuta casos de uso."""

import logging

from src.application.use_cases.gym_use_cases import GymUseCases
from src.domain.entities.gym import Cliente
from src.interfaces.http.schemas.gym_schema import ClienteInput, ClienteResponse
from src.interfaces.http.schemas.list_query import ClienteQuery

logger = logging.getLogger(__name__)


def list_clientes(use_cases: GymUseCases, query: ClienteQuery) -> list[ClienteResponse]:
    entities = use_cases.list(Cliente, query.offset, query.limit, query.to_filters())
    return [ClienteResponse.model_validate(entity) for entity in entities]


def get_cliente(use_cases: GymUseCases, entity_id: int) -> ClienteResponse:
    entity = use_cases.get(Cliente, entity_id)
    return ClienteResponse.model_validate(entity)


def create_cliente(use_cases: GymUseCases, data: ClienteInput) -> ClienteResponse:
    entity = use_cases.create(Cliente(**data.model_dump()))
    logger.info("Cliente creado: id=%s email=%s", entity.id_cliente, entity.email)
    return ClienteResponse.model_validate(entity)


def update_cliente(
    use_cases: GymUseCases, entity_id: int, data: ClienteInput
) -> ClienteResponse:
    entity = use_cases.update(Cliente, entity_id, Cliente(**data.model_dump()))
    return ClienteResponse.model_validate(entity)


def delete_cliente(use_cases: GymUseCases, entity_id: int) -> None:
    use_cases.delete(Cliente, entity_id)
    logger.info("Cliente eliminado: id=%s", entity_id)
