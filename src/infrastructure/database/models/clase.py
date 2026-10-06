"""Modelo SQLAlchemy de las clases programadas."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


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
