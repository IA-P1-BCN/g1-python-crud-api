"""Controlador HTTP de entrenadores: convierte schemas y ejecuta casos de uso."""

import logging

from src.application.use_cases.cuenta_use_cases import CuentaUseCases
from src.application.use_cases.gym_use_cases import GymUseCases
from src.domain.entities.gym import Entrenador, IdentidadEntrenador
from src.interfaces.http.schemas.gym_schema import (
    EntrenadorCreate,
    EntrenadorInput,
    EntrenadorResponse,
)
from src.interfaces.http.schemas.list_query import EntrenadorQuery

logger = logging.getLogger(__name__)


def _response(
    entity: Entrenador, cuentas: dict[int, IdentidadEntrenador]
) -> EntrenadorResponse:
    cuenta = cuentas.get(
        entity.id_entrenador, IdentidadEntrenador(id_entrenador=entity.id_entrenador)
    )
    return EntrenadorResponse(
        id_entrenador=entity.id_entrenador,
        nombre=entity.nombre,
        especialidad=entity.especialidad,
        telefono=entity.telefono,
        id_user=cuenta.id_user,
        email=cuenta.email,
    )


def _cuentas(
    use_cases: GymUseCases, entities: list[Entrenador]
) -> dict[int, IdentidadEntrenador]:
    return use_cases.accounts_for_entrenadores(
        [
            entity.id_entrenador
            for entity in entities
            if entity.id_entrenador is not None
        ]
    )


def list_entrenadores(
    use_cases: GymUseCases, query: EntrenadorQuery
) -> list[EntrenadorResponse]:
    entities = use_cases.list(
        Entrenador, query.offset, query.limit, query.to_filters()
    )
    cuentas = _cuentas(use_cases, entities)
    return [_response(entity, cuentas) for entity in entities]


def get_entrenador(use_cases: GymUseCases, entity_id: int) -> EntrenadorResponse:
    entity = use_cases.get(Entrenador, entity_id)
    cuentas = _cuentas(use_cases, [entity])
    return _response(entity, cuentas)


def create_entrenador(
    gym: GymUseCases, cuenta: CuentaUseCases, data: EntrenadorCreate
) -> EntrenadorResponse:
    if data.email is not None:
        nueva = cuenta.registrar_entrenador(
            data.nombre, data.especialidad, data.telefono, data.email
        )
        logger.info(
            "Entrenador creado con Cuenta: id=%s user=%s",
            nueva.id_entrenador,
            nueva.id,
        )
        return EntrenadorResponse(
            id_entrenador=nueva.id_entrenador,
            nombre=data.nombre,
            especialidad=data.especialidad,
            telefono=data.telefono,
            id_user=nueva.id,
            email=nueva.email,
        )
    entity = gym.create(Entrenador(**data.model_dump(exclude={"email"})))
    logger.info(
        "Entrenador creado: id=%s nombre=%s", entity.id_entrenador, entity.nombre
    )
    cuentas = _cuentas(gym, [entity])
    return _response(entity, cuentas)


def update_entrenador(
    use_cases: GymUseCases, entity_id: int, data: EntrenadorInput
) -> EntrenadorResponse:
    entity = use_cases.update(Entrenador, entity_id, Entrenador(**data.model_dump()))
    cuentas = _cuentas(use_cases, [entity])
    return _response(entity, cuentas)


def delete_entrenador(use_cases: GymUseCases, entity_id: int) -> None:
    use_cases.delete(Entrenador, entity_id)
    logger.info("Entrenador eliminado: id=%s", entity_id)
