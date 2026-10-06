"""Modelo SQLAlchemy de los clientes del gimnasio."""

from datetime import date

from sqlalchemy import CheckConstraint, Date, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


class ClienteRecord(Base):
    __tablename__ = "clientes"
    __table_args__ = (
        UniqueConstraint("email", name="uq_clientes_email"),
        CheckConstraint(
            "estado_membresia IN ('Activo', 'Inactivo', 'Suspendido')",
            name="ck_clientes_estado_membresia",
        ),
    )

    id_cliente: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(150))
    fecha_inscripcion: Mapped[date | None] = mapped_column(Date)
    estado_membresia: Mapped[str] = mapped_column(String(20))
