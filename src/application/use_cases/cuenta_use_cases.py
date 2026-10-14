"""Casos de uso de identidad; depende únicamente del dominio."""

from src.domain.entities.cuenta import Cuenta
from src.domain.errors import ConflictError
from src.domain.repositories.cuenta_port import CuentaRepository
from src.domain.security import PasswordHasher


class CuentaUseCases:
    def __init__(self, repository: CuentaRepository, hasher: PasswordHasher) -> None:
        self._repository = repository
        self._hasher = hasher

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
