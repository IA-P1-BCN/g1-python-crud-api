"""Puerto de persistencia y transacciones para las entidades del gimnasio."""

from contextlib import AbstractContextManager
from typing import Protocol

from src.domain.entities.gym import GymEntity


class GymRepository(Protocol):
    def transaction(self) -> AbstractContextManager[None]: ...

    def list[T: GymEntity](
        self, entity_type: type[T], offset: int, limit: int
    ) -> list[T]: ...

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
