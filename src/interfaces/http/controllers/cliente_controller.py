"""Controlador HTTP de clientes: convierte schemas y ejecuta casos de uso."""

import logging

from src.application.use_cases.gym_use_cases import GymUseCases
from src.domain.entities.gym import Cliente
from src.domain.repositories.gym_port import GymRepository
from src.interfaces.http.schemas.gym_schema import ClienteInput, ClienteResponse

logger = logging.getLogger(__name__)


def list_clientes(
    repository: GymRepository, offset: int, limit: int
) -> list[ClienteResponse]:
    entities = GymUseCases(repository).list(Cliente, offset, limit)
    return [ClienteResponse.model_validate(entity) for entity in entities]


def get_cliente(repository: GymRepository, entity_id: int) -> ClienteResponse:
    entity = GymUseCases(repository).get(Cliente, entity_id)
    return ClienteResponse.model_validate(entity)


def create_cliente(repository: GymRepository, data: ClienteInput) -> ClienteResponse:
    entity = GymUseCases(repository).create(Cliente(**data.model_dump()))
    logger.info("Cliente creado: id=%s email=%s", entity.id_cliente, entity.email)
    return ClienteResponse.model_validate(entity)


def update_cliente(
    repository: GymRepository, entity_id: int, data: ClienteInput
) -> ClienteResponse:
    entity = GymUseCases(repository).update(
        Cliente, entity_id, Cliente(**data.model_dump())
    )
    return ClienteResponse.model_validate(entity)


def delete_cliente(repository: GymRepository, entity_id: int) -> None:
    GymUseCases(repository).delete(Cliente, entity_id)
    logger.info("Cliente eliminado: id=%s", entity_id)
