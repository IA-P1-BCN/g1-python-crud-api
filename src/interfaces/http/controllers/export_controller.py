"""Controlador HTTP de exportación: resuelve la tabla y ejecuta el caso de uso."""

from src.application.use_cases.gym_use_cases import GymUseCases
from src.domain.entities.gym import GymEntity
from src.interfaces.http.csv_exports import TABLES, ExportTable


def export_table(use_cases: GymUseCases, tablas: ExportTable) -> list[GymEntity]:
    """Devuelve todas las filas de la tabla solicitada, ordenadas por ID."""
    return use_cases.list_all(TABLES[tablas])
