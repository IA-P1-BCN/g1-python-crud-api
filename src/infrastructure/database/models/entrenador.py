"""Modelo SQLAlchemy de los entrenadores del gimnasio."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


class EntrenadorRecord(Base):
    __tablename__ = "entrenadores"

    id_entrenador: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100))
    especialidad: Mapped[str | None] = mapped_column(String(100))
    telefono: Mapped[str | None] = mapped_column(String(20))
