"""Exportación CSV contra MySQL real (mismo aislamiento por test que el CRUD)."""

from uuid import uuid4

import httpx
import pytest
from sqlalchemy import delete, inspect, text
from sqlalchemy.exc import OperationalError

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


@pytest.fixture
def api(mysql_ready, base_url, gym_admin_headers):
    with httpx.Client(
        base_url=base_url, headers=gym_admin_headers, timeout=10
    ) as client:
        ids = {resource: [] for resource, _, _ in TABLES}

        def create(resource, data):
            response = client.post(f"/v1/{resource}", json=data)
            assert response.status_code == 201, response.text
            id_field = next(field for name, field, _ in TABLES if name == resource)
            ids[resource].append(response.json()[id_field])
            return response.json()

        try:
            yield client, create
        finally:
            # Solo borra IDs creados por este test, respetando las FK.
            with SessionLocal.begin() as session:
                for resource, id_field, model in TABLES:
                    session.execute(
                        delete(model).where(getattr(model, id_field).in_(ids[resource]))
                    )


def test_export_clientes(api):
    client, create = api
    for nombre in ["Ana García", "Àngels Pérez"]:
        create(
            "clientes",
            {
                "nombre": nombre,
                "email": f"{uuid4().hex}@example.com",
                "estado_membresia": "Activo",
                "fecha_inscripcion": "2026-10-01",
            },
        )
    response = client.get("/v1/export/csv", params={"tablas": "clientes"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert (
        response.headers["content-disposition"] == 'attachment; filename="clientes.csv"'
    )
    assert response.content.startswith(b"\xef\xbb\xbf")
    lineas = response.content.decode("utf-8-sig").split("\r\n")
    assert lineas[0] == "id_cliente,nombre,estado_membresia,email,fecha_inscripcion"
    assert [linea for linea in lineas if "Àngels Pérez" in linea]


def test_export_reservas(api):
    client, create = api
    cliente = create(
        "clientes",
        {
            "nombre": "Cliente de prueba",
            "email": f"{uuid4().hex}@example.com",
            "estado_membresia": "Activo",
        },
    )
    create(
        "pagos",
        {
            "id_cliente": cliente["id_cliente"],
            "monto": "30.50",
            "fecha_pago": "2026-10-06",
            "metodo_pago": "Efectivo",
        },
    )
    entrenador = create("entrenadores", {"nombre": "Entrenador de prueba"})
    clase = create(
        "clases",
        {
            "nombre_clase": "Yoga de prueba",
            "horario": "2026-11-01T10:00:00",
            "capacidad_max": 10,
            "id_entrenador": entrenador["id_entrenador"],
        },
    )
    reserva = create(
        "reservas",
        {"id_cliente": cliente["id_cliente"], "id_clase": clase["id_clase"]},
    )
    response = client.get("/v1/export/csv", params={"tablas": "reservas"})
    assert response.status_code == 200
    assert response.content.startswith(b"\xef\xbb\xbf")
    lineas = response.content.decode("utf-8-sig").split("\r\n")
    assert lineas[0] == "id_reserva,id_cliente,id_clase,fecha_reserva,asistio"
    fila = next(
        linea for linea in lineas if linea.startswith(f"{reserva['id_reserva']},")
    )
    assert fila.endswith(",False")
