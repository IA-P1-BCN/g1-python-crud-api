"""Puertos de seguridad sin dependencia de librerías criptográficas."""

from typing import Protocol


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...

    def verify(self, password: str, password_hash: str) -> bool: ...


class AccessTokens(Protocol):
    def issue(self, cuenta_id: int) -> str: ...

    def subject(self, token: str) -> int: ...
