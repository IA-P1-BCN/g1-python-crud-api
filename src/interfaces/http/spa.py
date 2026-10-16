"""Archivos de Angular y fallback de sus rutas, sin ocultar errores de la API."""

from pathlib import Path

from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles

SPA_ROUTES = {
    "",
    "portal",
    "login",
    "registro",
    "clases",
    "reservas",
    "clientes",
    "entrenadores",
    "gestion-clases",
    "pagos",
    "cuentas",
    "perfil",
    "export",
}


class SPAFiles(StaticFiles):
    async def get_response(self, path, scope):
        try:
            return await super().get_response(path, scope)
        except HTTPException as error:
            first_segment = path.strip("/").split("/", 1)[0]
            if (
                error.status_code == 404
                and scope["method"] in {"GET", "HEAD"}
                and first_segment in SPA_ROUTES
                and not Path(path).suffix
            ):
                return await super().get_response("index.html", scope)
            raise


def mount_spa(app: FastAPI, directory: Path) -> None:
    """El desarrollo sin build no necesita archivos de frontend."""
    if (directory / "index.html").is_file():
        app.mount("/", SPAFiles(directory=directory, html=True), name="frontend")
