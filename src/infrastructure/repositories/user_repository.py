"""Persistencia SQLAlchemy con confirmación antes de devolver la respuesta."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from src.domain.entities.user import User
from src.domain.errors import ConflictError, RepositoryUnavailableError
from src.infrastructure.database.models import UserRecord


class SqlAlchemyUserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    @contextmanager
    def transaction(self) -> Iterator[None]:
        try:
            with self.session.begin():
                yield
        except IntegrityError as exc:
            raise ConflictError(
                "La operación entra en conflicto con un usuario existente"
            ) from exc
        except OperationalError as exc:
            raise RepositoryUnavailableError("Base de datos no disponible") from exc

    def get(self, user_id: int, *, lock: bool = False) -> User | None:
        statement = select(UserRecord).where(UserRecord.id == user_id)
        if lock:
            statement = statement.with_for_update()
        record = self.session.scalar(statement)
        return self._entity(record) if record is not None else None

    def get_by_email(self, email: str) -> User | None:
        record = self.session.scalar(
            select(UserRecord).where(UserRecord.email == email)
        )
        return self._entity(record) if record is not None else None

    def list(self, offset: int, limit: int) -> list[User]:
        records = self.session.scalars(
            select(UserRecord).order_by(UserRecord.id).offset(offset).limit(limit)
        )
        return [self._entity(record) for record in records]

    def add(self, user: User) -> User:
        record = UserRecord(
            name=user.name,
            email=user.email,
            password_hash=user.password_hash,
            created_at=user.created_at.astimezone(UTC).replace(tzinfo=None),
            is_active=user.is_active,
            role=user.role,
            token_version=user.token_version,
        )
        self.session.add(record)
        self.session.flush()
        self.session.refresh(record)
        return self._entity(record)

    def update(self, user: User) -> User:
        record = self.session.get(UserRecord, user.id)
        record.name = user.name
        record.email = user.email
        record.password_hash = user.password_hash
        record.is_active = user.is_active
        record.token_version = user.token_version
        self.session.flush()
        self.session.refresh(record)
        return self._entity(record)

    def delete(self, user: User) -> None:
        self.session.delete(self.session.get(UserRecord, user.id))
        self.session.flush()

    @staticmethod
    def _entity(record: UserRecord) -> User:
        return User(
            id=record.id,
            name=record.name,
            email=record.email,
            password_hash=record.password_hash,
            created_at=record.created_at.replace(tzinfo=UTC),
            is_active=record.is_active,
            role=record.role,
            token_version=record.token_version,
        )
