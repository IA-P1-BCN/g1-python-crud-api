"""Modelo SQLAlchemy de los pagos de clientes."""

from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


class PagoRecord(Base):
    __tablename__ = "pagos"
    __table_args__ = (
        CheckConstraint("monto > 0", name="ck_pagos_monto"),
        CheckConstraint(
            "metodo_pago IN ('Tarjeta', 'Transferencia', 'Efectivo')",
            name="ck_pagos_metodo_pago",
        ),
    )

    id_pago: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_cliente: Mapped[int] = mapped_column(
        ForeignKey("clientes.id_cliente", ondelete="RESTRICT"), index=True
    )
    monto: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    fecha_pago: Mapped[date] = mapped_column(Date)
    metodo_pago: Mapped[str | None] = mapped_column(String(30))
