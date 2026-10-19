"""Modelo SQLAlchemy de los clientes del gimnasio.

La identidad (nombre, email) vive exclusivamente en `users` (ADR 0002);
`clientes` guarda solo el perfil de negocio.
"""

from datetime import date

from sqlalchemy import CheckConstraint, Date, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


class ClienteRecord(Base):
    __tablename__ = "clientes"
    __table_args__ = (
        CheckConstraint(
            "estado_membresia IN ('Activo', 'Inactivo', 'Suspendido')",
            name="ck_clientes_estado_membresia",
        ),
    )

    id_cliente: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fecha_inscripcion: Mapped[date | None] = mapped_column(Date)
    estado_membresia: Mapped[str] = mapped_column(String(20))
