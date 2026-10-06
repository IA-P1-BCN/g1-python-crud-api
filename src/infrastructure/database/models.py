"""Modelos SQLAlchemy (tablas gestionadas por las migraciones de Alembic)."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarativa de los modelos SQLAlchemy."""


class VersionRecord(Base):
    """Fila de la tabla `versions`: versión del esquema aplicada."""

    __tablename__ = "versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    applied_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )


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


class EntrenadorRecord(Base):
    __tablename__ = "entrenadores"

    id_entrenador: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100))
    especialidad: Mapped[str | None] = mapped_column(String(100))
    telefono: Mapped[str | None] = mapped_column(String(20))


class ClaseRecord(Base):
    __tablename__ = "clases"
    __table_args__ = (
        CheckConstraint("capacidad_max > 0", name="ck_clases_capacidad_max"),
    )

    id_clase: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre_clase: Mapped[str] = mapped_column(String(50))
    horario: Mapped[datetime] = mapped_column(DateTime)
    capacidad_max: Mapped[int] = mapped_column(Integer)
    id_entrenador: Mapped[int] = mapped_column(
        ForeignKey("entrenadores.id_entrenador", ondelete="RESTRICT"), index=True
    )


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
