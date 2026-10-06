"""Repositorio en memoria para probar HTTP y negocio sin MySQL."""

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from main import app
from src.domain.entities.gym import ID_FIELDS, Clase, Cliente, Entrenador, Pago, Reserva
from src.interfaces.http.dependencies import get_gym_repository


class MemoryRepository:
    def __init__(self):
        self.data = {entity: {} for entity in ID_FIELDS}
        self.sequences = {entity: 0 for entity in ID_FIELDS}

    @contextmanager
    def transaction(self):
        snapshot = deepcopy(self.data)
        try:
            yield
        except Exception:
            self.data = snapshot
            raise

    def list(self, entity_type, offset, limit):
        return list(self.data[entity_type].values())[offset : offset + limit]

    def get(self, entity_type, entity_id, *, lock=False):
        return self.data[entity_type].get(entity_id)

    def add(self, entity):
        entity_type = type(entity)
        self.sequences[entity_type] += 1
        entity_id = self.sequences[entity_type]
        stored = replace(entity, **{ID_FIELDS[entity_type]: entity_id})
        self.data[entity_type][entity_id] = stored
        return stored

    def update(self, entity):
        self.data[type(entity)][getattr(entity, ID_FIELDS[type(entity)])] = entity
        return entity

    def delete(self, entity):
        del self.data[type(entity)][getattr(entity, ID_FIELDS[type(entity)])]

    def count_reservas(self, id_clase, exclude_id=None):
        return sum(
            item.id_clase == id_clase and item.id_reserva != exclude_id
            for item in self.data[Reserva].values()
        )

    def has_pago(self, id_cliente):
        return any(item.id_cliente == id_cliente for item in self.data[Pago].values())

    def has_reserva(self, id_cliente, id_clase, exclude_id=None):
        return any(
            item.id_cliente == id_cliente
            and item.id_clase == id_clase
            and item.id_reserva != exclude_id
            for item in self.data[Reserva].values()
        )


@pytest.fixture
def repository():
    repo = MemoryRepository()
    repo.add(Cliente(nombre="Ana", estado_membresia="Activo"))
    repo.add(Entrenador(nombre="Luis", especialidad="Yoga"))
    repo.add(
        Clase(
            nombre_clase="Yoga",
            horario=datetime(2026, 11, 1, 10, tzinfo=UTC).replace(tzinfo=None),
            capacidad_max=10,
            id_entrenador=1,
        )
    )
    repo.add(Pago(id_cliente=1, monto=Decimal("25.00"), fecha_pago=date(2026, 10, 1)))
    return repo


@pytest.fixture
def client(repository):
    app.dependency_overrides[get_gym_repository] = lambda: repository
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_gym_repository, None)
