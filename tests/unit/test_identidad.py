"""La identidad (nombre/email) se resuelve de la Cuenta vinculada (ADR 0002)."""

from datetime import date
from decimal import Decimal

from src.domain.entities.gym import Cliente, Pago


def test_cliente_resuelve_identidad_del_user(client):
    detalle = client.get("/v1/clientes/1")
    assert detalle.status_code == 200
    cuerpo = detalle.json()
    assert cuerpo["id_user"] == 10
    assert cuerpo["nombre"] == "Ana"
    assert cuerpo["email"] == "ana@example.com"
    listado = client.get("/v1/clientes").json()
    assert listado[0]["nombre"] == "Ana"


def test_cliente_sin_cuenta_devuelve_identidad_null(client):
    creado = client.post("/v1/clientes", json={"estado_membresia": "Activo"})
    assert creado.status_code == 201
    cuerpo = creado.json()
    assert cuerpo["id_user"] is None
    assert cuerpo["nombre"] is None
    assert cuerpo["email"] is None


def test_cliente_rechaza_identidad_en_el_cuerpo(client):
    respuesta = client.post(
        "/v1/clientes",
        json={"estado_membresia": "Activo", "nombre": "Ana", "email": "a@example.com"},
    )
    assert respuesta.status_code == 422


def test_reserva_incluye_persona(client):
    creada = client.post(
        "/v1/reservas", json={"id_cliente": 1, "id_clase": 1, "asistio": False}
    )
    assert creada.status_code == 201, creada.text
    cuerpo = creada.json()
    assert cuerpo["id_user"] == 10
    assert cuerpo["nombre"] == "Ana"
    assert cuerpo["email"] == "ana@example.com"
    detalle = client.get(f"/v1/reservas/{cuerpo['id_reserva']}")
    assert detalle.json()["email"] == "ana@example.com"


def test_reserva_de_cliente_sin_cuenta_persona_null(client, repository):
    repository.add(Cliente(estado_membresia="Activo"))
    repository.add(
        Pago(id_cliente=2, monto=Decimal("25.00"), fecha_pago=date(2026, 10, 1))
    )
    creada = client.post(
        "/v1/reservas", json={"id_cliente": 2, "id_clase": 1, "asistio": False}
    )
    assert creada.status_code == 201
    cuerpo = creada.json()
    assert cuerpo["id_user"] is None
    assert cuerpo["nombre"] is None
    assert cuerpo["email"] is None
