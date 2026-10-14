"""Parámetros de listado: solo se convierten campos declarados en filtros."""

from datetime import date
from typing import Annotated, ClassVar, Literal

from pydantic import Field, NaiveDatetime

from src.domain.list_filters import ListFilters
from src.interfaces.http.schemas.gym_schema import ApiSchema

TextFilter = Annotated[str, Field(min_length=1, max_length=150)]
PositiveId = Annotated[int, Field(gt=0, le=2147483647)]


class ListQuery(ApiSchema):
    text_fields: ClassVar[tuple[str, ...]] = ()
    exact_fields: ClassVar[tuple[str, ...]] = ()
    range_field: ClassVar[str | None] = None

    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=100)

    def to_filters(self) -> ListFilters:
        return ListFilters(
            contains=tuple(
                (name, value)
                for name in self.text_fields
                if (value := getattr(self, name)) is not None
            ),
            equals=tuple(
                (name, value)
                for name in self.exact_fields
                if (value := getattr(self, name)) is not None
            ),
            date_field=self.range_field,
            date_from=getattr(self, f"{self.range_field}_desde", None),
            date_to=getattr(self, f"{self.range_field}_hasta", None),
            search=getattr(self, "q", None),
        )


class TextQuery(ListQuery):
    q: TextFilter | None = Field(
        default=None,
        description="Fragmento literal en los campos de texto; ignora mayúsculas",
    )


class CuentaQuery(TextQuery):
    text_fields = ("nombre", "email")
    exact_fields = ("activo", "rol", "id_cliente")
    range_field = "fecha_creacion"

    nombre: TextFilter | None = None
    email: TextFilter | None = None
    activo: bool | None = None
    rol: Literal["admin", "staff", "cliente"] | None = None
    id_cliente: PositiveId | None = None
    fecha_creacion_desde: NaiveDatetime | None = Field(
        default=None, description="Inicio inclusivo, UTC sin zona"
    )
    fecha_creacion_hasta: NaiveDatetime | None = Field(
        default=None, description="Fin inclusivo, UTC sin zona"
    )


class ClienteQuery(TextQuery):
    text_fields = ("nombre", "email")
    exact_fields = ("estado_membresia",)
    range_field = "fecha_inscripcion"

    nombre: TextFilter | None = None
    email: TextFilter | None = None
    estado_membresia: Literal["Activo", "Inactivo", "Suspendido"] | None = None
    fecha_inscripcion_desde: date | None = Field(default=None, description="Inclusiva")
    fecha_inscripcion_hasta: date | None = Field(default=None, description="Inclusiva")


class EntrenadorQuery(TextQuery):
    text_fields = ("nombre", "especialidad", "telefono")

    nombre: TextFilter | None = None
    especialidad: TextFilter | None = None
    telefono: TextFilter | None = None


class ClaseQuery(TextQuery):
    text_fields = ("nombre_clase",)
    exact_fields = ("id_entrenador",)
    range_field = "horario"

    nombre_clase: TextFilter | None = None
    id_entrenador: PositiveId | None = None
    horario_desde: NaiveDatetime | None = Field(
        default=None, description="Inicio inclusivo, UTC sin sufijo de zona"
    )
    horario_hasta: NaiveDatetime | None = Field(
        default=None, description="Fin inclusivo, UTC sin sufijo de zona"
    )


class ReservaQuery(ListQuery):
    exact_fields = ("id_cliente", "id_clase", "asistio")
    range_field = "fecha_reserva"

    id_cliente: PositiveId | None = None
    id_clase: PositiveId | None = None
    asistio: bool | None = None
    fecha_reserva_desde: NaiveDatetime | None = Field(
        default=None, description="Inicio inclusivo, UTC sin sufijo de zona"
    )
    fecha_reserva_hasta: NaiveDatetime | None = Field(
        default=None, description="Fin inclusivo, UTC sin sufijo de zona"
    )


class PagoQuery(ListQuery):
    exact_fields = ("id_cliente", "metodo_pago")
    range_field = "fecha_pago"

    id_cliente: PositiveId | None = None
    metodo_pago: Literal["Tarjeta", "Transferencia", "Efectivo"] | None = None
    fecha_pago_desde: date | None = Field(default=None, description="Inclusiva")
    fecha_pago_hasta: date | None = Field(default=None, description="Inclusiva")
