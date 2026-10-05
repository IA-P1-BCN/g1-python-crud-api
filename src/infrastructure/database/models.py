"""Modelos SQLAlchemy (tablas gestionadas por las migraciones de Alembic)."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
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
