"""Puerto de persistencia de Cuentas y altas de perfil opcionales."""

from contextlib import AbstractContextManager
from typing import Protocol

from src.domain.entities.cuenta import Cuenta


class CuentaRepository(Protocol):
    def transaction(self) -> AbstractContextManager[None]: ...

    def get_by_email(self, email: str) -> Cuenta | None: ...

    def add(self, cuenta: Cuenta) -> Cuenta: ...

    def create_cliente(self, nombre: str, email: str) -> int: ...
