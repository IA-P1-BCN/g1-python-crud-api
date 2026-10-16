"""Tokens de acceso firmados con algoritmo, emisor y audiencia fijos."""

from datetime import UTC, datetime, timedelta

import jwt

from src.domain.errors import AuthenticationError


class JwtAccessTokens:
    def __init__(self, secret: str, expire_minutes: int = 30) -> None:
        if len(secret) < 32:
            raise ValueError("SECRET_KEY requiere al menos 32 caracteres")
        self._secret = secret
        if type(expire_minutes) is not int or not 1 <= expire_minutes <= 1440:
            raise ValueError("La duración debe ser un entero entre 1 y 1440 minutos")
        self._expire_minutes = expire_minutes

    def issue(self, cuenta_id: int) -> str:
        now = datetime.now(UTC)
        return jwt.encode(
            {
                "sub": str(cuenta_id),
                "iat": now,
                "exp": now + timedelta(minutes=self._expire_minutes),
                "iss": "gymflow",
                "aud": "gymflow-api",
            },
            self._secret,
            algorithm="HS256",
        )

    def subject(self, token: str) -> int:
        try:
            claims = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"],
                issuer="gymflow",
                audience="gymflow-api",
                options={"require": ["sub", "iat", "exp", "iss", "aud"]},
            )
            subject = claims["sub"]
            if not subject.isascii() or not subject.isdecimal():
                raise ValueError("subject inválido")
            cuenta_id = int(subject)
            if not 0 < cuenta_id <= 2147483647:
                raise ValueError("subject fuera de rango")
            return cuenta_id
        except (jwt.InvalidTokenError, ValueError, OverflowError) as exc:
            raise AuthenticationError(
                "No se pudieron validar las credenciales"
            ) from exc
