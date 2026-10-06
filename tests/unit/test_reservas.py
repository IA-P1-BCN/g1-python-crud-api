"""Reglas de admisión, aforo y cambios de una reserva."""

from dataclasses import replace
from datetime import UTC, datetime

import pytest

from src.application.use_cases.gym_use_cases import GymUseCases
from src.domain.entities.gym import Clase, Cliente, Pago, Reserva
from src.domain.errors import ConflictError


def reserva(**changes):
    return Reserva(
        **(
            {
                "id_cliente": 1,
                "id_clase": 1,
                "fecha_reserva": datetime(2026, 10, 6, tzinfo=UTC).replace(tzinfo=None),
            }
            | changes
        )
    )


@pytest.mark.parametrize("estado", ["Inactivo", "Suspendido"])
def test_cliente_no_activo_no_reserva(repository, estado):
    repository.update(replace(repository.get(Cliente, 1), estado_membresia=estado))
    with pytest.raises(ConflictError, match="activos"):
        GymUseCases(repository).create(reserva())
    assert repository.data[Reserva] == {}


def test_cliente_sin_pagos_no_reserva(repository):
    repository.data[Pago].clear()
    with pytest.raises(ConflictError, match="pago"):
        GymUseCases(repository).create(reserva())
    assert repository.data[Reserva] == {}


def test_no_admite_reserva_duplicada(repository):
    use_cases = GymUseCases(repository)
    use_cases.create(reserva())
    with pytest.raises(ConflictError, match="ya tiene"):
        use_cases.create(reserva())
    assert repository.count_reservas(1) == 1


def test_no_admite_clase_llena(repository):
    repository.update(replace(repository.get(Clase, 1), capacidad_max=1))
    # La plaza ya está ocupada por otro cliente.
    repository.add(reserva(id_cliente=2))
    with pytest.raises(ConflictError, match="plazas"):
        GymUseCases(repository).create(reserva())


def test_no_reduce_aforo_por_debajo_de_reservas(repository):
    repository.add(reserva())
    repository.add(reserva(id_cliente=2))
    with pytest.raises(ConflictError, match="menor"):
        GymUseCases(repository).update(
            Clase, 1, replace(repository.get(Clase, 1), capacidad_max=1)
        )
    assert repository.get(Clase, 1).capacidad_max == 10


def test_actualiza_asistencia_de_cliente_ahora_inactivo(repository):
    use_cases = GymUseCases(repository)
    previous = use_cases.create(reserva())
    repository.update(replace(repository.get(Cliente, 1), estado_membresia="Inactivo"))
    updated = use_cases.update(Reserva, previous.id_reserva, reserva(asistio=True))
    assert updated.asistio is True
    assert updated.fecha_reserva == previous.fecha_reserva


def test_cambiar_a_clase_llena_conserva_reserva_original(repository):
    use_cases = GymUseCases(repository)
    previous = use_cases.create(reserva())
    target = repository.add(replace(repository.get(Clase, 1), capacidad_max=1))
    repository.add(reserva(id_cliente=2, id_clase=target.id_clase))
    with pytest.raises(ConflictError, match="plazas"):
        use_cases.update(
            Reserva, previous.id_reserva, reserva(id_clase=target.id_clase)
        )
    assert repository.get(Reserva, previous.id_reserva) == previous
