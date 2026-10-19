"""Exportación de tabla a CSV descargable (media type text/csv)."""

import csv
from enum import StrEnum
from io import StringIO

from fastapi import Response

from src.domain.entities.gym import Clase, Cliente, Entrenador, GymEntity, Pago, Reserva


class ExportTable(StrEnum):
    """Tablas admitidas por `GET /v1/export/csv?tablas=<tabla>`."""

    clientes = "clientes"
    entrenadores = "entrenadores"
    clases = "clases"
    reservas = "reservas"
    pagos = "pagos"


# Nombre de tabla -> entidad de dominio que se consulta con `list_all`.
TABLES: dict[ExportTable, type[GymEntity]] = {
    ExportTable.clientes: Cliente,
    ExportTable.entrenadores: Entrenador,
    ExportTable.clases: Clase,
    ExportTable.reservas: Reserva,
    ExportTable.pagos: Pago,
}

# Columnas de exportación por entidad, con el ID primero (orden amigable en Excel).
CSV_FIELDS: dict[type[GymEntity], list[str]] = {
    Cliente: ["id_cliente", "estado_membresia", "fecha_inscripcion"],
    Entrenador: ["id_entrenador", "nombre", "especialidad", "telefono"],
    Clase: ["id_clase", "nombre_clase", "horario", "capacidad_max", "id_entrenador"],
    Reserva: ["id_reserva", "id_cliente", "id_clase", "fecha_reserva", "asistio"],
    Pago: ["id_pago", "id_cliente", "monto", "fecha_pago", "metodo_pago"],
}


def to_csv(entity_type: type[GymEntity], entities: list[GymEntity]) -> bytes:
    """Convierte entidades en CSV con cabecera, terminador CRLF y BOM UTF-8."""
    buffer = StringIO()
    writer = csv.writer(buffer, lineterminator="\r\n")
    writer.writerow(CSV_FIELDS[entity_type])
    for entity in entities:
        writer.writerow(getattr(entity, name) for name in CSV_FIELDS[entity_type])
    # BOM (utf-8-sig) para que Excel muestre bien las tildes.
    return buffer.getvalue().encode("utf-8-sig")


def csv_response(
    resource: str, entity_type: type[GymEntity], entities: list[GymEntity]
) -> Response:
    """Respuesta descargable con nombre `<resource>.csv`."""
    headers = {"Content-Disposition": f'attachment; filename="{resource}.csv"'}
    return Response(
        content=to_csv(entity_type, entities), media_type="text/csv", headers=headers
    )


def export_response(tablas: ExportTable, entities: list[GymEntity]) -> Response:
    """Respuesta CSV de la tabla indicada (resuelve la entidad en `TABLES`)."""
    return csv_response(tablas.value, TABLES[tablas], entities)
