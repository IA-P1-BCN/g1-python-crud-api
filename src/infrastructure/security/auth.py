"""Argon2 para contraseñas y JWT HS256 para tokens de acceso."""

from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from src.domain.entities.user import AccessToken, TokenIdentity, User
from src.domain.errors import AuthenticationError


class Argon2Passwords:
    def __init__(self) -> None:
        self._hasher = PasswordHash.recommended()
        self._dummy_hash = self._hasher.hash(token_urlsafe(32))

    def hash(self, password: str) -> str:
        return self._hasher.hash(password)

    def verify(self, password: str, password_hash: str | None) -> bool:
        if len(password) > 128:
            return False
        try:
            valid = self._hasher.verify(password, password_hash or self._dummy_hash)
        except UnknownHashError, ValueError:
            return False
        return valid and password_hash is not None


class JwtTokens:
    def __init__(self, secret: str, expire_minutes: int) -> None:
        self._secret = secret
        self._expire_minutes = expire_minutes

    def create(self, user: User) -> AccessToken:
        now = datetime.now(UTC)
        token = jwt.encode(
            {
                "sub": str(user.id),
                "iat": now,
                "exp": now + timedelta(minutes=self._expire_minutes),
                "ver": user.token_version,
                "iss": "g1-user-api",
                "aud": "g1-user-api",
            },
            self._secret,
            algorithm="HS256",
        )
        return AccessToken(token, self._expire_minutes * 60)

    def decode(self, token: str) -> TokenIdentity:
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"],
                issuer="g1-user-api",
                audience="g1-user-api",
                options={"require": ["sub", "iat", "exp", "ver"]},
            )
            user_id = int(payload["sub"])
            version = payload["ver"]
            if user_id <= 0 or type(version) is not int or version < 0:
                raise ValueError("Identidad inválida")
            return TokenIdentity(user_id, version)
        except (InvalidTokenError, ValueError, TypeError) as exc:
            raise AuthenticationError(
                "No se pudieron validar las credenciales"
            ) from exc
