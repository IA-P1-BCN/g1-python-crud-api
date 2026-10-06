"""HTTP sin MySQL con repositorio en memoria y criptografía real."""

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from main import app
from src.application.use_cases.user_use_cases import UserUseCases
from src.domain.entities.user import User
from src.infrastructure.security.auth import Argon2Passwords, JwtTokens
from src.interfaces.http.dependencies import get_user_use_cases

TEST_SECRET = "unit-test-secret-only-000000000000000000000000"
ADMIN_PASSWORD = "Admin-Password-For-Tests-123"


class MemoryUsers:
    def __init__(self):
        self.data = {}
        self.sequence = 0

    @contextmanager
    def transaction(self):
        snapshot = deepcopy(self.data)
        try:
            yield
        except Exception:
            self.data = snapshot
            raise

    def get(self, user_id, *, lock=False):
        return self.data.get(user_id)

    def get_by_email(self, email):
        return next((user for user in self.data.values() if user.email == email), None)

    def list(self, offset, limit):
        return list(self.data.values())[offset : offset + limit]

    def add(self, user):
        self.sequence += 1
        user = replace(user, id=self.sequence)
        self.data[user.id] = user
        return user

    def update(self, user):
        self.data[user.id] = user
        return user

    def delete(self, user):
        del self.data[user.id]


@pytest.fixture(scope="module")
def passwords():
    return Argon2Passwords()


@pytest.fixture
def repository(passwords):
    repo = MemoryUsers()
    repo.add(
        User(
            name="Admin",
            email="admin@example.com",
            role="admin",
            password_hash=passwords.hash(ADMIN_PASSWORD),
            created_at=datetime.now(UTC),
        )
    )
    return repo


@pytest.fixture
def tokens():
    return JwtTokens(TEST_SECRET, 30)


@pytest.fixture
def use_cases(repository, passwords, tokens):
    return UserUseCases(repository, passwords, tokens)


@pytest.fixture
def client(use_cases):
    app.dependency_overrides[get_user_use_cases] = lambda: use_cases
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_user_use_cases, None)


@pytest.fixture
def admin_headers(repository, tokens):
    return {"Authorization": f"Bearer {tokens.create(repository.get(1)).access_token}"}
