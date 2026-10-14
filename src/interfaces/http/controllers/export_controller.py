"""Controlador HTTP de exportación: resuelve la tabla y ejecuta el caso de uso."""

from src.application.use_cases.gym_use_cases import GymUseCases
from src.domain.entities.gym import GymEntity
from src.domain.repositories.gym_port import GymRepository
from src.interfaces.http.csv_exports import TABLES, ExportTable


def export_table(repository: GymRepository, tablas: ExportTable) -> list[GymEntity]:
    """Devuelve todas las filas de la tabla solicitada, ordenadas por ID."""
    return GymUseCases(repository).list_all(TABLES[tablas])
