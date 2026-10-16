"""Matriz de acceso, filtros y ataques de cambio de propietario por HTTP."""

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from main import app
from src.domain.entities.gym import Clase, Cliente, Entrenador, Pago, Reserva
from src.interfaces.http.dependencies import get_gym_repository


@pytest.fixture
def secured_gym(authenticated_accounts, repository):
    client, accounts, _ = authenticated_accounts
    repository.add(Cliente(nombre="Otro", estado_membresia="Activo"))
    repository.add(Entrenador(nombre="Otra entrenadora"))
    for trainer in (2, 1):
        repository.add(
            Clase(
                nombre_clase="Otra clase",
                horario=datetime(2026, 11, 2, tzinfo=UTC).replace(tzinfo=None),
                capacidad_max=10,
                id_entrenador=trainer,
            )
        )
    repository.add(
        Pago(id_cliente=2, monto=Decimal(25), fecha_pago=date(2026, 10, 1))
    )
    for member, group in ((1, 1), (2, 2), (2, 1), (1, 3)):
        repository.add(
            Reserva(
                id_cliente=member, id_clase=group, fecha_reserva=datetime(2026, 10, 1, tzinfo=UTC).replace(tzinfo=None)
            )
        )
    app.dependency_overrides[get_gym_repository] = lambda: repository
    try:
        yield client, repository, accounts.cuentas[0]
    finally:
        app.dependency_overrides.pop(get_gym_repository, None)


def actor_role(actor, role):
    actor.rol = role
    actor.id_cliente = 1 if role == "cliente" else None
    actor.id_entrenador = 1 if role == "staff" else None


@pytest.mark.parametrize(
    "role,resource,field,expected",
    [
        ("admin", "clientes", "id_cliente", [1, 2]),
        ("admin", "reservas", "id_reserva", [1, 2, 3, 4]),
        ("cliente", "clientes", "id_cliente", [1]),
        ("cliente", "pagos", "id_pago", [1]),
        ("cliente", "reservas", "id_reserva", [1, 4]),
        ("cliente", "clases", "id_clase", [1, 2, 3]),
        ("cliente", "entrenadores", "id_entrenador", [1, 2]),
        ("staff", "clases", "id_clase", [1, 3]),
        ("staff", "reservas", "id_reserva", [1, 3, 4]),
        ("staff", "entrenadores", "id_entrenador", [1]),
        ("staff", "clientes", "id_cliente", None),
        ("staff", "pagos", "id_pago", None),
    ],
)
def test_listados_segun_actor(secured_gym, role, resource, field, expected):
    client, _, actor = secured_gym
    actor_role(actor, role)
    response = client.get(f"/v1/{resource}")
    assert response.status_code == (403 if expected is None else 200)
    if expected is not None:
        assert [row[field] for row in response.json()] == expected


@pytest.mark.parametrize("role,second", [("cliente", 4), ("staff", 3)])
def test_alcance_antes_de_paginar_y_filtros_no_amplian(secured_gym, role, second):
    client, _, actor = secured_gym
    actor_role(actor, role)
    response = client.get("/v1/reservas", params={"offset": 1, "limit": 1})
    assert [r["id_reserva"] for r in response.json()] == [second]
    foreign_filter = {"id_cliente": 2} if role == "cliente" else {"id_clase": 2}
    assert client.get("/v1/reservas", params=foreign_filter).json() == []
    assert client.get("/v1/reservas/2").status_code == 404
    assert client.delete("/v1/reservas/2").status_code == 404
    assert (
        client.put("/v1/reservas/2", json={"id_cliente": 1, "id_clase": 1}).status_code
        == 404
    )


@pytest.mark.parametrize("role", ["staff", "cliente"])
def test_sin_vinculo_no_recibe_datos_propios(secured_gym, role):
    client, _, actor = secured_gym
    actor_role(actor, role)
    actor.id_cliente = actor.id_entrenador = None
    assert client.get("/v1/reservas").json() == []
    assert client.get("/v1/reservas/1").status_code == 404
    assert (
        client.post("/v1/reservas", json={"id_cliente": 1, "id_clase": 1}).status_code
        == 403
    )


@pytest.mark.parametrize("role", ["staff", "cliente"])
@pytest.mark.parametrize(
    "table", ["clientes", "entrenadores", "clases", "reservas", "pagos"]
)
def test_exportacion_solo_admin(secured_gym, role, table):
    client, _, actor = secured_gym
    actor_role(actor, role)
    response = client.get("/v1/export/csv", params={"tablas": table})
    assert (
        response.status_code == 403
        and "text/csv" not in response.headers["content-type"]
    )


def test_cliente_reserva_solo_lo_suyo_y_no_marca_asistencia(secured_gym):
    client, repository, actor = secured_gym
    actor_role(actor, "cliente")
    for body in (
        {"id_cliente": 2, "id_clase": 3},
        {"id_cliente": 1, "id_clase": 2, "asistio": True},
    ):
        assert client.post("/v1/reservas", json=body).status_code == 403
        assert client.put("/v1/reservas/1", json=body).status_code == 403
    assert len(repository.data[Reserva]) == 4
    assert client.get("/v1/pagos/2").status_code == 404
    assert client.get("/v1/clientes/2").status_code == 404
    assert (
        client.post(
            "/v1/pagos",
            json={
                "id_cliente": 1,
                "monto": "100",
                "fecha_pago": "2026-10-16",
            },
        ).status_code
        == 403
    )
    assert (
        client.put(
            "/v1/clientes/1", json={"nombre": "X", "estado_membresia": "Activo"}
        ).status_code
        == 403
    )
    created = client.post("/v1/reservas", json={"id_cliente": 1, "id_clase": 2})
    assert created.status_code == 201
    assert (
        client.delete(f"/v1/reservas/{created.json()['id_reserva']}").status_code == 204
    )
    assert client.get("/v1/clases/1/cupo").json() == {
        "id_clase": 1,
        "capacidad_max": 10,
        "reservas": 2,
        "plazas_disponibles": 8,
    }


def test_staff_no_reasigna_clases_ni_mueve_reservas_fuera_de_su_alcance(secured_gym):
    client, repository, actor = secured_gym
    actor_role(actor, "staff")
    foreign = {
        "nombre_clase": "Otra",
        "horario": "2026-11-01T10:00:00",
        "capacidad_max": 10,
        "id_entrenador": 2,
    }
    assert client.post("/v1/clases", json=foreign).status_code == 403
    assert client.put("/v1/clases/1", json=foreign).status_code == 403
    assert client.get("/v1/clases/2/cupo").status_code == 404
    assert client.delete("/v1/clases/2").status_code == 404
    assert (
        client.put("/v1/reservas/1", json={"id_cliente": 1, "id_clase": 2}).status_code
        == 403
    )
    assert repository.data[Reserva][1].id_clase == 1
    result = client.put(
        "/v1/reservas/1", json={"id_cliente": 1, "id_clase": 1, "asistio": True}
    )
    assert result.status_code == 200 and result.json()["asistio"] is True
    assert (
        client.post("/v1/clases", json=foreign | {"id_entrenador": 1}).status_code
        == 201
    )
