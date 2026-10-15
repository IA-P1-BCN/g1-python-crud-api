"""Casos de uso de identidad; depende únicamente del dominio."""

from dataclasses import replace

from src.domain.entities.cuenta import Cuenta
from src.domain.errors import ConflictError, NotFoundError
from src.domain.repositories.cuenta_port import CuentaRepository
from src.domain.security import PasswordHasher


class CuentaUseCases:
    def __init__(self, repository: CuentaRepository, hasher: PasswordHasher) -> None:
        self._repository = repository
        self._hasher = hasher

    def list(self, offset: int = 0, limit: int = 100) -> list[Cuenta]:
        with self._repository.transaction():
            return self._repository.list(offset, limit)

    def get(self, cuenta_id: int) -> Cuenta:
        with self._repository.transaction():
            return self._require(cuenta_id)

    def delete(self, cuenta_id: int) -> None:
        with self._repository.transaction():
            self._repository.delete(self._require(cuenta_id, lock=True))

    def _require(self, cuenta_id: int, *, lock: bool = False) -> Cuenta:
        cuenta = self._repository.get(cuenta_id, lock=lock)
        if cuenta is None:
            raise NotFoundError(f"Cuenta con id {cuenta_id} no existe")
        return cuenta

    def update(
        self,
        cuenta_id: int,
        nombre: str | None = None,
        email: str | None = None,
        password: str | None = None,
    ) -> Cuenta:
        with self._repository.transaction():
            previous = self._require(cuenta_id, lock=True)
            cuenta = replace(previous)
            if nombre is not None:
                cuenta.nombre = nombre
            if email is not None:
                cuenta.email = email.lower()
                existing = self._repository.get_by_email(cuenta.email)
                if existing is not None and existing.id != cuenta_id:
                    raise ConflictError("Email de Cuenta ya registrado")
            if password is not None:
                cuenta.password_hash = self._hasher.hash(password)
            return self._repository.update(cuenta)

    def register(
        self, nombre: str, email: str, password: str, crear_cliente: bool = False
    ) -> Cuenta:
        cuenta = Cuenta(
            nombre=nombre,
            email=email.lower(),
            password_hash=self._hasher.hash(password),
        )
        with self._repository.transaction():
            if self._repository.get_by_email(cuenta.email) is not None:
                raise ConflictError("Email de Cuenta ya registrado")
            if crear_cliente:
                cuenta.id_cliente = self._repository.create_cliente(
                    nombre, cuenta.email
                )
            return self._repository.add(cuenta)
