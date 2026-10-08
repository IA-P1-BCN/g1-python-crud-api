"""Controlador HTTP de pagos: convierte schemas y ejecuta casos de uso."""

import logging

from src.application.use_cases.gym_use_cases import GymUseCases
from src.domain.entities.gym import Pago
from src.domain.repositories.gym_port import GymRepository
from src.interfaces.http.schemas.gym_schema import PagoInput, PagoResponse

logger = logging.getLogger(__name__)


def list_pagos(
    repository: GymRepository, offset: int, limit: int
) -> list[PagoResponse]:
    entities = GymUseCases(repository).list(Pago, offset, limit)
    return [PagoResponse.model_validate(entity) for entity in entities]


def get_pago(repository: GymRepository, entity_id: int) -> PagoResponse:
    entity = GymUseCases(repository).get(Pago, entity_id)
    return PagoResponse.model_validate(entity)


def create_pago(repository: GymRepository, data: PagoInput) -> PagoResponse:
    entity = GymUseCases(repository).create(Pago(**data.model_dump()))
    logger.info("Pago creado: id=%s cliente_id=%s monto=%s", entity.id_pago, entity.id_cliente, entity.monto)
    return PagoResponse.model_validate(entity)


def update_pago(
    repository: GymRepository, entity_id: int, data: PagoInput
) -> PagoResponse:
    entity = GymUseCases(repository).update(Pago, entity_id, Pago(**data.model_dump()))
    return PagoResponse.model_validate(entity)


def delete_pago(repository: GymRepository, entity_id: int) -> None:
    GymUseCases(repository).delete(Pago, entity_id)
    logger.info("Pago eliminado: id=%s", entity_id)
