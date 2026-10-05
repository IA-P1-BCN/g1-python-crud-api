"""Implementación del puerto HealthRepository sobre SQLAlchemy."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.infrastructure.database.engine import SessionLocal
from src.infrastructure.database.models import VersionRecord


class SqlAlchemyHealthRepository:
    """Consulta el estado de MySQL y la versión del esquema."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def ping(self) -> bool:
        """Ejecuta SELECT 1 para confirmar que la conexión está viva."""
        self._session.execute(text("SELECT 1"))
        return True

    def get_latest_version(self) -> str | None:
        """Lee la versión más reciente de la tabla `versions`."""
        registro = (
            self._session.query(VersionRecord)
            .order_by(VersionRecord.applied_at.desc(), VersionRecord.id.desc())
            .first()
        )
        return registro.version if registro is not None else None


def get_health_repository() -> SqlAlchemyHealthRepository:
    """Dependencia FastAPI: crea sesión y repositorio, y cierra al finalizar."""
    with SessionLocal() as session:
        yield SqlAlchemyHealthRepository(session)
