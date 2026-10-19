"""Adaptador SQLAlchemy para el CRUD y sus transacciones."""

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict, fields

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from src.domain.entities.gym import (
    ID_FIELDS,
    Clase,
    Cliente,
    Entrenador,
    GymEntity,
    IdentidadCliente,
    Pago,
    Reserva,
)
from src.domain.errors import ConflictError, RepositoryUnavailableError
from src.domain.gym_scope import GymScope
from src.domain.list_filters import SEARCH_FIELDS, ListFilters
from src.infrastructure.database.models import (
    ClaseRecord,
    ClienteRecord,
    CuentaRecord,
    EntrenadorRecord,
    PagoRecord,
    ReservaRecord,
)

MODELS = {
    Cliente: ClienteRecord,
    Entrenador: EntrenadorRecord,
    Clase: ClaseRecord,
    Reserva: ReservaRecord,
    Pago: PagoRecord,
}


from src.infrastructure.repositories.listing import apply_list_filters


class SqlAlchemyGymRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """Confirma antes de responder; cualquier error revierte la operación."""
        try:
            with self._session.begin():
                yield
        except IntegrityError as exc:
            raise ConflictError(
                "La operación entra en conflicto con un registro o relación existente"
            ) from exc
        except OperationalError as exc:
            code = exc.orig.args[0] if exc.orig.args else None
            if code in {1205, 1213}:
                raise ConflictError(
                    "Otro cambio concurrente impidió la operación; inténtalo de nuevo"
                ) from exc
            raise RepositoryUnavailableError("Base de datos no disponible") from exc

    def list[T: GymEntity](
        self,
        entity_type: type[T],
        offset: int,
        limit: int,
        filters: ListFilters | None = None,
        scope: GymScope | None = None,
    ) -> list[T]:
        model = MODELS[entity_type]
        statement = apply_list_filters(
            select(model), model, filters, SEARCH_FIELDS.get(entity_type, ())
        )
        if scope is not None:
            if scope.id_cliente is not None:
                statement = statement.where(model.id_cliente == scope.id_cliente)
            if scope.id_entrenador is not None:
                if entity_type is Reserva:
                    own_classes = select(ClaseRecord.id_clase).where(
                        ClaseRecord.id_entrenador == scope.id_entrenador
                    )
                    statement = statement.where(ReservaRecord.id_clase.in_(own_classes))
                else:
                    statement = statement.where(
                        model.id_entrenador == scope.id_entrenador
                    )
        statement = (
            statement.order_by(getattr(model, ID_FIELDS[entity_type]))
            .offset(offset)
            .limit(limit)
        )
        return [
            self._entity(entity_type, record)
            for record in self._session.scalars(statement)
        ]

    def list_all[T: GymEntity](self, entity_type: type[T]) -> list[T]:
        model = MODELS[entity_type]
        statement = select(model).order_by(getattr(model, ID_FIELDS[entity_type]))
        return [
            self._entity(entity_type, record)
            for record in self._session.scalars(statement)
        ]

    def get[T: GymEntity](
        self, entity_type: type[T], entity_id: int, *, lock: bool = False
    ) -> T | None:
        model = MODELS[entity_type]
        statement = select(model).where(
            getattr(model, ID_FIELDS[entity_type]) == entity_id
        )
        if lock:
            statement = statement.with_for_update()
        record = self._session.scalar(statement)
        return None if record is None else self._entity(entity_type, record)

    def add[T: GymEntity](self, entity: T) -> T:
        record = MODELS[type(entity)](**asdict(entity))
        self._session.add(record)
        self._session.flush()
        self._session.refresh(record)
        return self._entity(type(entity), record)

    def update[T: GymEntity](self, entity: T) -> T:
        model = MODELS[type(entity)]
        record = self._session.get(model, getattr(entity, ID_FIELDS[type(entity)]))
        for name, value in asdict(entity).items():
            setattr(record, name, value)
        self._session.flush()
        self._session.refresh(record)
        return self._entity(type(entity), record)

    def delete(self, entity: GymEntity) -> None:
        record = self._session.get(
            MODELS[type(entity)], getattr(entity, ID_FIELDS[type(entity)])
        )
        self._session.delete(record)
        self._session.flush()

    def identities_for_clientes(
        self, id_clientes: list[int]
    ) -> dict[int, IdentidadCliente]:
        if not id_clientes:
            return {}
        statement = select(
            CuentaRecord.id,
            CuentaRecord.nombre,
            CuentaRecord.email,
            CuentaRecord.id_cliente,
        ).where(CuentaRecord.id_cliente.in_(id_clientes))
        return {
            row.id_cliente: IdentidadCliente(
                id_cliente=row.id_cliente,
                id_user=row.id,
                nombre=row.nombre,
                email=row.email,
            )
            for row in self._session.execute(statement)
        }

    def count_reservas(self, id_clase: int, exclude_id: int | None = None) -> int:
        statement = (
            select(func.count())
            .select_from(ReservaRecord)
            .where(ReservaRecord.id_clase == id_clase)
        )
        if exclude_id is not None:
            statement = statement.where(ReservaRecord.id_reserva != exclude_id)
        return self._session.scalar(statement)

    def has_pago(self, id_cliente: int) -> bool:
        statement = (
            select(PagoRecord.id_pago)
            .where(PagoRecord.id_cliente == id_cliente)
            .limit(1)
        )
        return self._session.scalar(statement) is not None

    def has_reserva(
        self, id_cliente: int, id_clase: int, exclude_id: int | None = None
    ) -> bool:
        statement = select(ReservaRecord.id_reserva).where(
            ReservaRecord.id_cliente == id_cliente,
            ReservaRecord.id_clase == id_clase,
        )
        if exclude_id is not None:
            statement = statement.where(ReservaRecord.id_reserva != exclude_id)
        return self._session.scalar(statement.limit(1)) is not None

    @staticmethod
    def _entity[T: GymEntity](entity_type: type[T], record: object) -> T:
        return entity_type(
            **{field.name: getattr(record, field.name) for field in fields(entity_type)}
        )
