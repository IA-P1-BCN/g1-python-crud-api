"""Usuarios e identidad de sesión, independientes de HTTP y SQLAlchemy."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True, kw_only=True)
class User:
    name: str
    email: str
    password_hash: str = field(repr=False)
    created_at: datetime
    is_active: bool = True
    role: str = "user"
    token_version: int = field(default=0, repr=False)
    id: int | None = None


@dataclass(frozen=True)
class TokenIdentity:
    user_id: int
    version: int


@dataclass(frozen=True)
class AccessToken:
    access_token: str = field(repr=False)
    expires_in: int
    token_type: str = "bearer"


@dataclass(frozen=True, kw_only=True)
class UserUpdate:
    name: str
    email: str
    is_active: bool
    password: str | None = field(default=None, repr=False)
