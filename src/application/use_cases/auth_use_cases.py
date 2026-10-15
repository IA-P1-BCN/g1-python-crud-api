"""Autenticación independiente del transporte y de la librería JWT."""

from src.domain.entities.cuenta import Cuenta
from src.domain.errors import AuthenticationError, ForbiddenError
from src.domain.repositories.cuenta_port import CuentaRepository
from src.domain.security import AccessTokens, PasswordHasher


class AuthUseCases:
    def __init__(
        self,
        repository: CuentaRepository,
        hasher: PasswordHasher,
        tokens: AccessTokens,
        dummy_hash: str,
    ) -> None:
        self._repository = repository
        self._hasher = hasher
        self._tokens = tokens
        self._dummy_hash = dummy_hash

    def login(self, email: str, password: str) -> str:
        with self._repository.transaction():
            cuenta = self._repository.get_by_email(email.strip().lower())
        password_hash = cuenta.password_hash if cuenta else self._dummy_hash
        valid = self._hasher.verify(password, password_hash)
        if cuenta is None or not valid or not cuenta.activo:
            raise AuthenticationError("Credenciales incorrectas")
        return self._tokens.issue(cuenta.id)

    def current_user(self, token: str | None) -> Cuenta:
        if not token:
            raise AuthenticationError("No se pudieron validar las credenciales")
        cuenta_id = self._tokens.subject(token)
        with self._repository.transaction():
            cuenta = self._repository.get(cuenta_id)
        if cuenta is None:
            raise AuthenticationError("No se pudieron validar las credenciales")
        if not cuenta.activo:
            raise ForbiddenError("La Cuenta está inactiva")
        return cuenta
