"""Repositorio en memoria para probar HTTP y negocio sin MySQL."""

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from main import app
from src.domain.entities.cuenta import Cuenta
from src.domain.entities.gym import (
    ID_FIELDS,
    Clase,
    Cliente,
    Entrenador,
    IdentidadCliente,
    IdentidadEntrenador,
    Pago,
    Reserva,
)
from src.domain.list_filters import SEARCH_FIELDS
from src.interfaces.http.dependencies import (
    get_cuenta_repository,
    get_current_user,
    get_gym_repository,
)


class MemoryRepository:
    def __init__(self):
        self.data = {entity: {} for entity in ID_FIELDS}
        self.sequences = {entity: 0 for entity in ID_FIELDS}
        self.identities: dict[int, IdentidadCliente] = {}
        self.staff_accounts: dict[int, IdentidadEntrenador] = {}

    @contextmanager
    def transaction(self):
        snapshot = deepcopy(self.data)
        try:
            yield
        except Exception:
            self.data = snapshot
            raise

    def identities_for_clientes(self, id_clientes):
        return {
            id_cliente: identidad
            for id_cliente, identidad in self.identities.items()
            if id_cliente in id_clientes
        }

    def accounts_for_entrenadores(self, id_entrenadores):
        return {
            id_entrenador: cuenta
            for id_entrenador, cuenta in self.staff_accounts.items()
            if id_entrenador in id_entrenadores
        }

    def list(self, entity_type, offset, limit, filters=None, scope=None):
        rows = list(self.data[entity_type].values())
        if scope is not None:
            if scope.id_cliente is not None:
                rows = [r for r in rows if r.id_cliente == scope.id_cliente]
            if scope.id_entrenador is not None:
                if entity_type is Reserva:
                    rows = [
                        r
                        for r in rows
                        if self.data[Clase][r.id_clase].id_entrenador
                        == scope.id_entrenador
                    ]
                else:
                    rows = [r for r in rows if r.id_entrenador == scope.id_entrenador]
        if filters:
            for name, value in filters.contains:
                rows = [
                    row
                    for row in rows
                    if value.lower() in (getattr(row, name) or "").lower()
                ]
            for name, value in filters.equals:
                rows = [row for row in rows if getattr(row, name) == value]
            if filters.date_field and filters.date_from is not None:
                rows = [
                    row
                    for row in rows
                    if (
                        getattr(row, filters.date_field) is not None
                        and getattr(row, filters.date_field) >= filters.date_from
                    )
                ]
            if filters.date_field and filters.date_to is not None:
                rows = [
                    row
                    for row in rows
                    if (
                        getattr(row, filters.date_field) is not None
                        and getattr(row, filters.date_field) <= filters.date_to
                    )
                ]
            if filters.search is not None:
                rows = [
                    row
                    for row in rows
                    if any(
                        filters.search.lower() in (getattr(row, name) or "").lower()
                        for name in SEARCH_FIELDS[entity_type]
                    )
                ]
        rows.sort(key=lambda row: getattr(row, ID_FIELDS[entity_type]))
        return rows[offset : offset + limit]

    def list_all(self, entity_type):
        return list(self.data[entity_type].values())

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
    repo.add(Cliente(estado_membresia="Activo"))
    repo.identities[1] = IdentidadCliente(
        id_cliente=1, id_user=10, nombre="Ana", email="ana@example.com"
    )
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
    app.dependency_overrides[get_current_user] = lambda: Cuenta(
        id=1,
        nombre="Admin",
        email="admin@example.com",
        password_hash="test",
        rol="admin",
    )
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_gym_repository, None)
        app.dependency_overrides.pop(get_current_user, None)


class RegistrationRepository:
    def __init__(self):
        self.cuentas = []

    @contextmanager
    def transaction(self):
        yield

    def get_by_email(self, email):
        return next((cuenta for cuenta in self.cuentas if cuenta.email == email), None)

    def delete(self, cuenta):
        self.cuentas = [row for row in self.cuentas if row.id != cuenta.id]

    def update(self, cuenta):
        index = next(
            i for i, current in enumerate(self.cuentas) if current.id == cuenta.id
        )
        self.cuentas[index] = cuenta
        return cuenta

    def get(self, cuenta_id, *, lock=False):
        return next((cuenta for cuenta in self.cuentas if cuenta.id == cuenta_id), None)

    def list(self, offset, limit, filters=None):
        return sorted(self.cuentas, key=lambda cuenta: cuenta.id)[
            offset : offset + limit
        ]

    def add(self, cuenta):
        cuenta = replace(cuenta, id=len(self.cuentas) + 1)
        self.cuentas.append(cuenta)
        return cuenta


@pytest.fixture
def registration_client():
    repository = RegistrationRepository()
    app.dependency_overrides[get_cuenta_repository] = lambda: repository
    try:
        with TestClient(app) as client:
            yield client, repository
    finally:
        app.dependency_overrides.pop(get_cuenta_repository, None)


@pytest.fixture
def authenticated_accounts(registration_client):
    client, repository = registration_client
    rows = [
        client.post(
            "/v1/auth/register",
            json={
                "nombre": f"Cuenta {i}",
                "email": f"cuenta{i}@example.com",
                "password": "contraseña de prueba",
            },
        ).json()
        for i in range(3)
    ]
    repository.cuentas[0].rol = "admin"
    rows[0]["rol"] = "admin"
    token = client.post(
        "/v1/auth/login",
        data={"username": rows[0]["email"], "password": "contraseña de prueba"},
    ).json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client, repository, rows
