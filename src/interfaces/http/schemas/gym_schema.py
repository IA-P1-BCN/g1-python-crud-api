"""Contratos HTTP del CRUD. PUT sustituye todos los campos editables."""

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, NaiveDatetime


class ApiSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, extra="forbid", str_strip_whitespace=True
    )


class ClienteInput(ApiSchema):
    nombre: str = Field(min_length=1, max_length=100, examples=["Ana García"])
    email: EmailStr | None = Field(default=None, max_length=150)
    estado_membresia: Literal["Activo", "Inactivo", "Suspendido"]
    fecha_inscripcion: date | None = None


class ClienteResponse(ClienteInput):
    id_cliente: int


class EntrenadorInput(ApiSchema):
    nombre: str = Field(min_length=1, max_length=100)
    especialidad: str | None = Field(default=None, min_length=1, max_length=100)
    telefono: str | None = Field(default=None, min_length=1, max_length=20)


class EntrenadorResponse(EntrenadorInput):
    id_entrenador: int


class ClaseInput(ApiSchema):
    nombre_clase: str = Field(min_length=1, max_length=50, examples=["Yoga"])
    horario: NaiveDatetime = Field(
        description="Fecha y hora UTC sin sufijo de zona horaria",
        examples=["2026-11-01T10:00:00"],
    )
    capacidad_max: int = Field(gt=0, le=2147483647)
    id_entrenador: int = Field(gt=0, le=2147483647)


class ClaseResponse(ClaseInput):
    id_clase: int


class ReservaInput(ApiSchema):
    id_cliente: int = Field(gt=0, le=2147483647)
    id_clase: int = Field(gt=0, le=2147483647)
    asistio: bool = False


class ReservaResponse(ReservaInput):
    id_reserva: int
    fecha_reserva: datetime = Field(
        description="Fecha UTC generada al crear la reserva"
    )


class PagoInput(ApiSchema):
    id_cliente: int = Field(gt=0, le=2147483647)
    monto: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
    fecha_pago: date
    metodo_pago: Literal["Tarjeta", "Transferencia", "Efectivo"] | None = None


class PagoResponse(PagoInput):
    id_pago: int


class ErrorResponse(BaseModel):
    detail: str
