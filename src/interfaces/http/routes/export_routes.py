"""Endpoint de exportación de datos a CSV."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response

from src.application.use_cases.gym_use_cases import GymUseCases
from src.interfaces.http.controllers import export_controller as controller
from src.interfaces.http.csv_exports import ExportTable, export_response
from src.interfaces.http.dependencies import get_gym_use_cases
from src.interfaces.http.errors import CRUD_ERRORS

router = APIRouter(prefix="/export", tags=["export"])
UseCases = Annotated[GymUseCases, Depends(get_gym_use_cases)]


@router.get(
    "/csv",
    response_class=Response,
    summary="Exporta una tabla a CSV",
    responses={
        200: {
            "description": "Archivo CSV con todos los registros de la tabla",
            "content": {"text/csv": {}},
        },
        **CRUD_ERRORS,
    },
)
def export_csv(tablas: ExportTable, use_cases: UseCases) -> Response:
    return export_response(tablas, controller.export_table(use_cases, tablas))
