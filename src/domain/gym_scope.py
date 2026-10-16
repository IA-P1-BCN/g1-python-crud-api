"""Alcance de acceso del actor, independiente de los filtros enviados por HTTP."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GymScope:
    id_cliente: int | None = None
    id_entrenador: int | None = None
