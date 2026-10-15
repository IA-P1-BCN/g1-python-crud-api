"""Persistencia de Cuenta; un Cliente puede tener como máximo una Cuenta."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


class CuentaRecord(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("id_cliente", name="uq_users_id_cliente"),
        CheckConstraint("rol IN ('admin', 'staff', 'cliente')", name="ck_users_rol"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150))
    password_hash: Mapped[str] = mapped_column(String(255))
    activo: Mapped[bool] = mapped_column(Boolean, server_default=text("1"))
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP")
    )
    rol: Mapped[str] = mapped_column(String(20), server_default="cliente")
    id_cliente: Mapped[int | None] = mapped_column(
        ForeignKey("clientes.id_cliente", ondelete="RESTRICT")
    )
