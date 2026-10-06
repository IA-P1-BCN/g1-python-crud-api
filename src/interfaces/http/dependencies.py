"""Wiring de los puertos de usuarios y obtención de la identidad autenticada."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config.settings import get_settings
from src.application.use_cases.user_use_cases import UserUseCases
from src.domain.entities.user import User
from src.infrastructure.database.engine import get_session
from src.infrastructure.repositories.user_repository import SqlAlchemyUserRepository
from src.infrastructure.security.auth import Argon2Passwords, JwtTokens

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")


@lru_cache
def get_passwords() -> Argon2Passwords:
    return Argon2Passwords()


def get_user_use_cases(
    session: Annotated[Session, Depends(get_session)],
    passwords: Annotated[Argon2Passwords, Depends(get_passwords)],
) -> UserUseCases:
    settings = get_settings()
    return UserUseCases(
        SqlAlchemyUserRepository(session),
        passwords,
        JwtTokens(
            settings.secret_key.get_secret_value(), settings.access_token_expire_minutes
        ),
    )


UseCases = Annotated[UserUseCases, Depends(get_user_use_cases)]


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], use_cases: UseCases
) -> User:
    return use_cases.authenticate(token)


CurrentUser = Annotated[User, Depends(get_current_user)]
