"""Exporta los modelos y registra todas las tablas en la metadata de Alembic."""

from src.infrastructure.database.models.base import Base
from src.infrastructure.database.models.clase import ClaseRecord
from src.infrastructure.database.models.cliente import ClienteRecord
from src.infrastructure.database.models.entrenador import EntrenadorRecord
from src.infrastructure.database.models.pago import PagoRecord
from src.infrastructure.database.models.reserva import ReservaRecord
from src.infrastructure.database.models.version import VersionRecord

__all__ = [
    "Base",
    "ClaseRecord",
    "ClienteRecord",
    "EntrenadorRecord",
    "PagoRecord",
    "ReservaRecord",
    "VersionRecord",
]
