"""Controlador HTTP de pagos: convierte schemas y ejecuta casos de uso."""

import logging

from src.application.use_cases.gym_use_cases import GymUseCases
from src.domain.entities.gym import Pago
from src.interfaces.http.schemas.gym_schema import PagoInput, PagoResponse
from src.interfaces.http.schemas.list_query import PagoQuery

logger = logging.getLogger(__name__)


def list_pagos(use_cases: GymUseCases, query: PagoQuery) -> list[PagoResponse]:
    entities = use_cases.list(Pago, query.offset, query.limit, query.to_filters())
    return [PagoResponse.model_validate(entity) for entity in entities]


def get_pago(use_cases: GymUseCases, entity_id: int) -> PagoResponse:
    entity = use_cases.get(Pago, entity_id)
    return PagoResponse.model_validate(entity)


def create_pago(use_cases: GymUseCases, data: PagoInput) -> PagoResponse:
    entity = use_cases.create(Pago(**data.model_dump()))
    logger.info(
        "Pago creado: id=%s cliente_id=%s monto=%s",
        entity.id_pago,
        entity.id_cliente,
        entity.monto,
    )
    return PagoResponse.model_validate(entity)


def update_pago(
    use_cases: GymUseCases, entity_id: int, data: PagoInput
) -> PagoResponse:
    entity = use_cases.update(Pago, entity_id, Pago(**data.model_dump()))
    return PagoResponse.model_validate(entity)


def delete_pago(use_cases: GymUseCases, entity_id: int) -> None:
    use_cases.delete(Pago, entity_id)
    logger.info("Pago eliminado: id=%s", entity_id)
