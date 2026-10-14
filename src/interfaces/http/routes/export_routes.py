"""Endpoint de exportación de datos a CSV."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response

from src.domain.repositories.gym_port import GymRepository
from src.interfaces.http.controllers import export_controller as controller
from src.interfaces.http.csv_exports import ExportTable, export_response
from src.interfaces.http.dependencies import get_gym_repository
from src.interfaces.http.errors import CRUD_ERRORS

router = APIRouter(prefix="/export", tags=["export"])
Repository = Annotated[GymRepository, Depends(get_gym_repository)]


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
def export_csv(tablas: ExportTable, repository: Repository) -> Response:
    return export_response(tablas, controller.export_table(repository, tablas))
