"""Adaptador SQLAlchemy de cuentas con transacciones atómicas."""

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict, fields
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from src.domain.entities.cuenta import Cuenta
from src.domain.errors import ConflictError, RepositoryUnavailableError
from src.infrastructure.database.models import ClienteRecord, CuentaRecord


class SqlAlchemyCuentaRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    @contextmanager
    def transaction(self) -> Iterator[None]:
        try:
            with self._session.begin():
                yield
        except IntegrityError as exc:
            raise ConflictError("Email o vínculo de Cuenta ya registrado") from exc
        except OperationalError as exc:
            if exc.orig.args and exc.orig.args[0] in {1205, 1213}:
                raise ConflictError("Cambio concurrente; inténtalo de nuevo") from exc
            raise RepositoryUnavailableError("Base de datos no disponible") from exc

    def get_by_email(self, email: str) -> Cuenta | None:
        record = self._session.scalar(
            select(CuentaRecord).where(CuentaRecord.email == email)
        )
        return self._entity(record) if record is not None else None

    def add(self, cuenta: Cuenta) -> Cuenta:
        record = CuentaRecord(**asdict(cuenta))
        self._session.add(record)
        self._session.flush()
        self._session.refresh(record)
        return self._entity(record)

    def get(self, cuenta_id: int, *, lock: bool = False) -> Cuenta | None:
        statement = select(CuentaRecord).where(CuentaRecord.id == cuenta_id)
        if lock:
            statement = statement.with_for_update()
        record = self._session.scalar(statement)
        return self._entity(record) if record is not None else None

    def create_cliente(self, nombre: str, email: str) -> int:
        record = ClienteRecord(
            nombre=nombre,
            email=email,
            estado_membresia="Inactivo",
            fecha_inscripcion=datetime.now(UTC).date(),
        )
        self._session.add(record)
        self._session.flush()
        return record.id_cliente

    @staticmethod
    def _entity(record: CuentaRecord) -> Cuenta:
        return Cuenta(**{f.name: getattr(record, f.name) for f in fields(Cuenta)})
