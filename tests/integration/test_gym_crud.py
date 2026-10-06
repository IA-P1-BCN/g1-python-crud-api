"""HTTP real contra MySQL migrado, con aislamiento de los datos de cada test."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import delete, inspect, text
from sqlalchemy.exc import OperationalError

from scripts.seed_gym import seed_demo
from src.infrastructure.database.engine import SessionLocal, engine
from src.infrastructure.database.models import (
    ClaseRecord,
    ClienteRecord,
    EntrenadorRecord,
    PagoRecord,
    ReservaRecord,
)

TABLES = [
    ("reservas", "id_reserva", ReservaRecord),
    ("pagos", "id_pago", PagoRecord),
    ("clases", "id_clase", ClaseRecord),
    ("clientes", "id_cliente", ClienteRecord),
    ("entrenadores", "id_entrenador", EntrenadorRecord),
]


@pytest.fixture(scope="module")
def mysql_ready():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError:
        pytest.skip("MySQL no disponible: ejecuta `task db:up && task migrate`")
    assert inspect(engine).has_table("clientes"), "Aplica las migraciones: task migrate"


class GymApi:
    def __init__(self, client):
        self.client = client
        self.ids = {resource: [] for resource, _, _ in TABLES}

    def post(self, resource, data):
        response = self.client.post(f"/v1/{resource}", json=data)
        if response.status_code == 201:
            id_field = next(field for name, field, _ in TABLES if name == resource)
            self.ids[resource].append(response.json()[id_field])
        return response

    def create(self, resource, data):
        response = self.post(resource, data)
        assert response.status_code == 201, response.text
        return response.json()

    def member(self, *, estado="Activo", paid=True):
        cliente = self.create(
            "clientes",
            {
                "nombre": "Cliente de prueba",
                "email": f"{uuid4().hex}@example.com",
                "estado_membresia": estado,
                "fecha_inscripcion": "2026-10-01",
            },
        )
        if paid:
            self.create(
                "pagos",
                {
                    "id_cliente": cliente["id_cliente"],
                    "monto": "30.50",
                    "fecha_pago": "2026-10-06",
                    "metodo_pago": "Efectivo",
                },
            )
        return cliente


@pytest.fixture
def api(mysql_ready, base_url):
    with httpx.Client(base_url=base_url, timeout=10) as client:
        api = GymApi(client)
        try:
            yield api
        finally:
            # Solo borra IDs creados por este test, respetando las FK.
            with SessionLocal.begin() as session:
                for resource, id_field, model in TABLES:
                    session.execute(
                        delete(model).where(
                            getattr(model, id_field).in_(api.ids[resource])
                        )
                    )


@pytest.fixture
def clase(api):
    entrenador = api.create("entrenadores", {"nombre": "Entrenador de prueba"})
    return api.create(
        "clases",
        {
            "nombre_clase": "Yoga de prueba",
            "horario": "2026-11-01T10:00:00",
            "capacidad_max": 2,
            "id_entrenador": entrenador["id_entrenador"],
        },
    )


def editable(entity, id_field):
    return {
        key: value
        for key, value in entity.items()
        if key not in {id_field, "fecha_reserva"}
    }


def test_crud_de_las_cinco_entidades(api, clase):
    cliente = api.member()
    pago = api.client.get(f"/v1/pagos/{api.ids['pagos'][0]}").json()
    entrenador = api.client.get(f"/v1/entrenadores/{clase['id_entrenador']}").json()
    reserva = api.create(
        "reservas",
        {
            "id_cliente": cliente["id_cliente"],
            "id_clase": clase["id_clase"],
        },
    )
    cases = [
        (
            "clientes",
            "id_cliente",
            cliente,
            {
                "nombre": "Nombre actualizado",
                "estado_membresia": "Suspendido",
                "fecha_inscripcion": None,
            },
        ),
        (
            "entrenadores",
            "id_entrenador",
            entrenador,
            {"especialidad": "Pilates", "telefono": "+34 600 000 000"},
        ),
        ("clases", "id_clase", clase, {"nombre_clase": "Pilates", "capacidad_max": 3}),
        ("pagos", "id_pago", pago, {"monto": "45.75", "metodo_pago": "Transferencia"}),
        ("reservas", "id_reserva", reserva, {"asistio": True}),
    ]
    for resource, id_field, entity, changes in cases:
        detail = f"/v1/{resource}/{entity[id_field]}"
        assert api.client.get(detail).json() == entity
        listed = api.client.get(f"/v1/{resource}")
        assert listed.status_code == 200
        assert entity in listed.json()
        updated = api.client.put(detail, json=editable(entity, id_field) | changes)
        assert updated.status_code == 200, updated.text
        for key, value in changes.items():
            assert updated.json()[key] == value
        if resource == "reservas":
            assert updated.json()["fecha_reserva"] == entity["fecha_reserva"]
        # Otra conexión HTTP lee lo confirmado, no una entidad en memoria.
        fetched = httpx.get(str(api.client.base_url.join(detail)), timeout=10)
        assert fetched.json() == updated.json()
    for resource, id_field, _ in TABLES:
        entity = next(case[2] for case in cases if case[0] == resource)
        detail = f"/v1/{resource}/{entity[id_field]}"
        response = api.client.delete(detail)
        assert response.status_code == 204, response.text
        assert response.content == b""
        assert api.client.get(detail).status_code == 404


def test_email_unico_y_rollback(api):
    cliente = api.member(paid=False)
    duplicate = api.post("clientes", editable(cliente, "id_cliente"))
    assert duplicate.status_code == 409
    assert set(duplicate.json()) == {"detail"}
    assert "INSERT" not in duplicate.text
    otro = api.member(paid=False)
    updated = api.client.put(
        f"/v1/clientes/{otro['id_cliente']}",
        json={
            **editable(otro, "id_cliente"),
            "email": cliente["email"],
        },
    )
    assert updated.status_code == 409
    assert api.client.get(f"/v1/clientes/{otro['id_cliente']}").json() == otro


@pytest.mark.parametrize(
    "estado,paid", [("Inactivo", True), ("Suspendido", True), ("Activo", False)]
)
def test_reserva_exige_cliente_activo_con_pago(api, clase, estado, paid):
    cliente = api.member(estado=estado, paid=paid)
    response = api.post(
        "reservas",
        {
            "id_cliente": cliente["id_cliente"],
            "id_clase": clase["id_clase"],
        },
    )
    assert response.status_code == 409


def test_duplicados_aforo_y_cancelacion(api, clase):
    clientes = [api.member() for _ in range(3)]
    payloads = [
        {"id_cliente": row["id_cliente"], "id_clase": clase["id_clase"]}
        for row in clientes
    ]
    primera = api.create("reservas", payloads[0])
    assert api.post("reservas", payloads[0]).status_code == 409
    api.create("reservas", payloads[1])
    assert api.post("reservas", payloads[2]).status_code == 409
    smaller = api.client.put(
        f"/v1/clases/{clase['id_clase']}",
        json={
            **editable(clase, "id_clase"),
            "capacidad_max": 1,
        },
    )
    assert smaller.status_code == 409
    assert (
        api.client.get(f"/v1/clases/{clase['id_clase']}").json()["capacidad_max"] == 2
    )
    assert api.client.delete(f"/v1/reservas/{primera['id_reserva']}").status_code == 204
    api.create("reservas", payloads[2])


def test_borrado_con_historial_se_bloquea(api, clase):
    cliente = api.member()
    api.create(
        "reservas", {"id_cliente": cliente["id_cliente"], "id_clase": clase["id_clase"]}
    )
    for resource, entity_id in [
        ("clientes", cliente["id_cliente"]),
        ("entrenadores", clase["id_entrenador"]),
        ("clases", clase["id_clase"]),
    ]:
        detail = f"/v1/{resource}/{entity_id}"
        assert api.client.delete(detail).status_code == 409
        assert api.client.get(detail).status_code == 200


def test_reservas_concurrentes_no_sobrevenden(api, clase):
    first, second = api.member(), api.member()
    response = api.client.put(
        f"/v1/clases/{clase['id_clase']}",
        json={
            **editable(clase, "id_clase"),
            "capacidad_max": 1,
        },
    )
    assert response.status_code == 200
    barrier = Barrier(2)

    def reserve(cliente):
        barrier.wait(timeout=5)
        return api.post(
            "reservas",
            {
                "id_cliente": cliente["id_cliente"],
                "id_clase": clase["id_clase"],
            },
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(reserve, [first, second]))
    assert sorted(response.status_code for response in results) == [201, 409]
    with SessionLocal() as session:
        count = session.execute(
            text("SELECT COUNT(*) FROM reservas WHERE id_clase = :id_clase"),
            {"id_clase": clase["id_clase"]},
        ).scalar_one()
    assert count == 1


def test_seed_repetido_no_duplica_ni_sobrescribe(mysql_ready):
    from sqlalchemy import func, select

    with SessionLocal() as session:
        try:
            seed_demo(session)
            counts = [
                session.scalar(select(func.count()).select_from(model))
                for _, _, model in TABLES
            ]
            ana = session.scalar(
                select(ClienteRecord).where(
                    ClienteRecord.email == "ana.demo@example.com"
                )
            )
            ana.nombre = "Nombre editado por el equipo"
            ana.estado_membresia = "Suspendido"
            seed_demo(session)
            assert [
                session.scalar(select(func.count()).select_from(model))
                for _, _, model in TABLES
            ] == counts
            session.refresh(ana)
            assert ana.nombre == "Nombre editado por el equipo"
            assert ana.estado_membresia == "Suspendido"
        finally:
            session.rollback()
