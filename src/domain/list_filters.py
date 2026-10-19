"""Criterios de consulta independientes del transporte y de la persistencia."""

from dataclasses import dataclass
from datetime import date, datetime

from src.domain.entities.gym import Clase, Cliente, Entrenador

SEARCH_FIELDS = {
    Cliente: (),
    Entrenador: ("nombre", "especialidad", "telefono"),
    Clase: ("nombre_clase",),
}


@dataclass(frozen=True, slots=True)
class ListFilters:
    contains: tuple[tuple[str, str], ...] = ()
    equals: tuple[tuple[str, str | int | bool], ...] = ()
    date_field: str | None = None
    date_from: date | datetime | None = None
    date_to: date | datetime | None = None
    search: str | None = None
