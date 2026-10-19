"""Tests de la exportación a CSV (sin base de datos)."""

from datetime import UTC, date, datetime
from decimal import Decimal

from fastapi import Response

from src.domain.entities.gym import Cliente, Entrenador, Pago, Reserva
from src.interfaces.http.csv_exports import csv_response, to_csv

BOM = b"\xef\xbb\xbf"


def _body(entity_type, entities) -> str:
    return to_csv(entity_type, entities).decode("utf-8-sig")


def test_cabecera_con_id_primero_y_bom():
    csv_bytes = to_csv(Cliente, [])
    assert csv_bytes.startswith(BOM)
    assert _body(Cliente, []) == "id_cliente,estado_membresia,fecha_inscripcion\r\n"


def test_escapado_de_comas_y_comillas():
    entrenador = Entrenador(
        nombre='García, "Ana"', especialidad="Yoga, restaurativo", id_entrenador=1
    )
    lineas = _body(Entrenador, [entrenador]).split("\r\n")
    assert lineas[1] == '1,"García, ""Ana""","Yoga, restaurativo",'


def test_formato_de_reserva():
    reserva = Reserva(
        id_cliente=1,
        id_clase=2,
        fecha_reserva=datetime(2026, 11, 1, 10, tzinfo=UTC).replace(tzinfo=None),
        asistio=True,
        id_reserva=3,
    )
    lineas = _body(Reserva, [reserva]).split("\r\n")
    assert lineas[0] == "id_reserva,id_cliente,id_clase,fecha_reserva,asistio"
    assert lineas[1] == "3,1,2,2026-11-01 10:00:00,True"


def test_formato_de_pago():
    pago = Pago(
        id_cliente=1,
        monto=Decimal("30.50"),
        fecha_pago=date(2026, 10, 6),
        metodo_pago="Tarjeta",
        id_pago=2,
    )
    lineas = _body(Pago, [pago]).split("\r\n")
    assert lineas[0] == "id_pago,id_cliente,monto,fecha_pago,metodo_pago"
    assert lineas[1] == "2,1,30.50,2026-10-06,Tarjeta"


def test_respuesta_descargable():
    clientes = [Cliente(estado_membresia="Activo", id_cliente=1)]
    response = csv_response("clientes", Cliente, clientes)
    assert isinstance(response, Response)
    assert response.media_type == "text/csv"
    assert response.headers["content-disposition"] == 'attachment; filename="clientes.csv"'
    assert response.body.startswith(BOM)


def test_endpoint_exporta_tabla(client):
    response = client.get("/v1/export/csv", params={"tablas": "clientes"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert response.headers["content-disposition"] == 'attachment; filename="clientes.csv"'
    assert response.content.startswith(BOM)
    assert "Activo" in response.content.decode("utf-8-sig")


def test_endpoint_tabla_inexistente_devuelve_422(client):
    response = client.get("/v1/export/csv", params={"tablas": "inventada"})
    assert response.status_code == 422


def test_endpoint_tabla_obligatoria(client):
    response = client.get("/v1/export/csv")
    assert response.status_code == 422