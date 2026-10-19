"""Puerto de persistencia y transacciones para las entidades del gimnasio."""

from contextlib import AbstractContextManager
from typing import Protocol

from src.domain.entities.gym import (
    GymEntity,
    IdentidadCliente,
    IdentidadEntrenador,
)
from src.domain.gym_scope import GymScope
from src.domain.list_filters import ListFilters


class GymRepository(Protocol):
    def transaction(self) -> AbstractContextManager[None]: ...

    def identities_for_clientes(
        self, id_clientes: list[int]
    ) -> dict[int, IdentidadCliente]: ...

    def accounts_for_entrenadores(
        self, id_entrenadores: list[int]
    ) -> dict[int, IdentidadEntrenador]: ...

    def list[T: GymEntity](
        self,
        entity_type: type[T],
        offset: int,
        limit: int,
        filters: ListFilters | None = None,
        scope: GymScope | None = None,
    ) -> list[T]: ...

    def list_all[T: GymEntity](self, entity_type: type[T]) -> list[T]: ...

    def get[T: GymEntity](
        self, entity_type: type[T], entity_id: int, *, lock: bool = False
    ) -> T | None: ...

    def add[T: GymEntity](self, entity: T) -> T: ...

    def update[T: GymEntity](self, entity: T) -> T: ...

    def delete(self, entity: GymEntity) -> None: ...

    def count_reservas(self, id_clase: int, exclude_id: int | None = None) -> int: ...

    def has_pago(self, id_cliente: int) -> bool: ...

    def has_reserva(
        self, id_cliente: int, id_clase: int, exclude_id: int | None = None
    ) -> bool: ...
