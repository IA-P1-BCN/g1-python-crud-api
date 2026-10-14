"""Identidad de acceso, independiente de la membresía del Cliente."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

Rol = Literal["admin", "staff", "cliente"]


@dataclass(slots=True, kw_only=True)
class Cuenta:
    nombre: str
    email: str
    password_hash: str = field(repr=False)
    id: int | None = None
    activo: bool = True
    rol: Rol = "cliente"
    id_cliente: int | None = None
    fecha_creacion: datetime = field(
        default_factory=lambda: datetime.now(UTC).replace(tzinfo=None)
    )
