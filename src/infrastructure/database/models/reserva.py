"""Modelo SQLAlchemy de las reservas y la asistencia."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


class ReservaRecord(Base):
    __tablename__ = "reservas"
    __table_args__ = (
        UniqueConstraint("id_cliente", "id_clase", name="uq_reservas_cliente_clase"),
    )

    id_reserva: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_cliente: Mapped[int] = mapped_column(
        ForeignKey("clientes.id_cliente", ondelete="RESTRICT"), index=True
    )
    id_clase: Mapped[int] = mapped_column(
        ForeignKey("clases.id_clase", ondelete="RESTRICT"), index=True
    )
    fecha_reserva: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    asistio: Mapped[bool] = mapped_column(Boolean, server_default="0")
