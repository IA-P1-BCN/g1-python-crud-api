"""Registro, autenticación y CRUD con permisos de propietario o administrador."""

from dataclasses import replace
from datetime import UTC, datetime

from src.domain.entities.user import AccessToken, User, UserUpdate
from src.domain.errors import (
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
)
from src.domain.repositories.user_port import (
    PasswordHasher,
    TokenProvider,
    UserRepository,
)


class UserUseCases:
    def __init__(
        self,
        repository: UserRepository,
        passwords: PasswordHasher,
        tokens: TokenProvider,
    ) -> None:
        self.repository = repository
        self.passwords = passwords
        self.tokens = tokens

    def register(self, name: str, email: str, password: str) -> User:
        user = User(
            name=name,
            email=email.strip().lower(),
            password_hash=self.passwords.hash(password),
            created_at=datetime.now(UTC),
        )
        with self.repository.transaction():
            if self.repository.get_by_email(user.email) is not None:
                raise ConflictError("Ya existe un usuario con ese email")
            return self.repository.add(user)

    def login(self, email: str, password: str) -> AccessToken:
        with self.repository.transaction():
            user = self.repository.get_by_email(email.strip().lower())
        # La verificación también se ejecuta para usuarios inexistentes/inactivos.
        valid = self.passwords.verify(password, user.password_hash if user else None)
        if not valid or user is None or not user.is_active:
            raise AuthenticationError("Email o contraseña incorrectos")
        return self.tokens.create(user)

    def authenticate(self, token: str) -> User:
        identity = self.tokens.decode(token)
        with self.repository.transaction():
            user = self.repository.get(identity.user_id)
        if user is None or not user.is_active or user.token_version != identity.version:
            raise AuthenticationError("No se pudieron validar las credenciales")
        return user

    def list(self, actor: User, offset: int, limit: int) -> list[User]:
        self._admin(actor)
        with self.repository.transaction():
            return self.repository.list(offset, limit)

    def get(self, actor: User, user_id: int) -> User:
        self._owner_or_admin(actor, user_id)
        with self.repository.transaction():
            return self._require(user_id)

    def create(self, actor: User, name: str, email: str, password: str) -> User:
        self._admin(actor)
        return self.register(name, email, password)

    def update(self, actor: User, user_id: int, data: UserUpdate) -> User:
        self._owner_or_admin(actor, user_id)
        new_hash = (
            self.passwords.hash(data.password) if data.password is not None else None
        )
        with self.repository.transaction():
            previous = self._require(user_id, lock=True)
            email = data.email.strip().lower()
            other = self.repository.get_by_email(email)
            if other is not None and other.id != user_id:
                raise ConflictError("Ya existe un usuario con ese email")
            invalidate = new_hash is not None or previous.is_active != data.is_active
            user = replace(
                previous,
                name=data.name,
                email=email,
                is_active=data.is_active,
                password_hash=new_hash or previous.password_hash,
                token_version=previous.token_version + int(invalidate),
            )
            return self.repository.update(user)

    def delete(self, actor: User, user_id: int) -> None:
        self._owner_or_admin(actor, user_id)
        with self.repository.transaction():
            self.repository.delete(self._require(user_id, lock=True))

    def _require(self, user_id: int, *, lock: bool = False) -> User:
        user = self.repository.get(user_id, lock=lock)
        if user is None:
            raise NotFoundError("Usuario no encontrado")
        return user

    @staticmethod
    def _admin(actor: User) -> None:
        if actor.role != "admin":
            raise ForbiddenError("Se requiere rol de administrador")

    @staticmethod
    def _owner_or_admin(actor: User, user_id: int) -> None:
        if actor.role != "admin" and actor.id != user_id:
            raise ForbiddenError("No tienes permiso para acceder a este usuario")
