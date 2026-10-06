"""Entidades de GymFlow según docs/DATABASE_SPEC.md y docs/PRD.md (V1)."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True, kw_only=True)
class Cliente:
    nombre: str
    estado_membresia: str
    email: str | None = None
    fecha_inscripcion: date | None = None
    id_cliente: int | None = None


@dataclass(frozen=True, kw_only=True)
class Entrenador:
    nombre: str
    especialidad: str | None = None
    telefono: str | None = None
    id_entrenador: int | None = None


@dataclass(frozen=True, kw_only=True)
class Clase:
    nombre_clase: str
    horario: datetime
    capacidad_max: int
    id_entrenador: int
    id_clase: int | None = None


@dataclass(frozen=True, kw_only=True)
class Reserva:
    id_cliente: int
    id_clase: int
    fecha_reserva: datetime
    asistio: bool = False
    id_reserva: int | None = None


@dataclass(frozen=True, kw_only=True)
class Pago:
    id_cliente: int
    monto: Decimal
    fecha_pago: date
    metodo_pago: str | None = None
    id_pago: int | None = None


type GymEntity = Cliente | Entrenador | Clase | Reserva | Pago

ID_FIELDS = {
    Cliente: "id_cliente",
    Entrenador: "id_entrenador",
    Clase: "id_clase",
    Reserva: "id_reserva",
    Pago: "id_pago",
}
