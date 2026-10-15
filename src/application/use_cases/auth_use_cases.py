"""Autenticación independiente del transporte y de la librería JWT."""

from src.domain.errors import AuthenticationError
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
