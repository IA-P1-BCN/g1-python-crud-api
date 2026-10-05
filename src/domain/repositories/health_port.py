"""Puerto de acceso a la base de datos para los healthchecks."""

from typing import Protocol


class HealthRepository(Protocol):
    """Contrato que implementa la infraestructura de persistencia."""

    def ping(self) -> bool:
        """Comprueba que la conexión a la base de datos está viva."""
        ...

    def get_latest_version(self) -> str | None:
        """Devuelve la última versión del esquema registrada, o None."""
        ...
