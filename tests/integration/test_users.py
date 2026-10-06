"""Registro, login y CRUD por HTTP real contra MySQL migrado."""

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from threading import Barrier
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import delete, inspect, select, text
from sqlalchemy.exc import OperationalError

from scripts.seed_users import seed_users
from src.infrastructure.database.engine import SessionLocal, engine
from src.infrastructure.database.models import UserRecord
from src.infrastructure.security.auth import Argon2Passwords

PASSWORD = "Integration-Password-12345"


@pytest.fixture(scope="module")
def mysql_ready():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError:
        pytest.skip("MySQL no disponible: ejecuta `task db:up && task migrate`")
    assert inspect(engine).has_table("users"), (
        "Falta la migración: ejecuta task migrate"
    )


class UserApi:
    def __init__(self, client):
        self.client = client
        self.ids = []
        self.admin_headers = {}

    def register(self, email=None, path="/v1/auth/register", headers=None):
        response = self.client.post(
            path,
            headers=headers,
            json={
                "name": "Usuario de prueba",
                "email": email or f"{uuid4().hex}@example.com",
                "password": PASSWORD,
            },
        )
        if response.status_code == 201:
            self.ids.append(response.json()["id"])
        return response

    def login(self, email, password=PASSWORD):
        return self.client.post(
            "/v1/auth/login", data={"username": email, "password": password}
        )

    def headers(self, email):
        response = self.login(email)
        assert response.status_code == 200, response.text
        return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture(scope="module")
def passwords():
    return Argon2Passwords()


@pytest.fixture
def api(mysql_ready, base_url, passwords):
    with httpx.Client(base_url=base_url, timeout=10) as client:
        api = UserApi(client)
        email = f"admin-{uuid4().hex}@example.com"
        with SessionLocal.begin() as session:
            admin = UserRecord(
                name="Admin de prueba",
                email=email,
                role="admin",
                is_active=True,
                password_hash=passwords.hash(PASSWORD),
                token_version=0,
                created_at=datetime.now(UTC).replace(tzinfo=None),
            )
            session.add(admin)
            session.flush()
            api.ids.append(admin.id)
        try:
            api.admin_headers = api.headers(email)
            yield api
        finally:
            with SessionLocal.begin() as session:
                session.execute(delete(UserRecord).where(UserRecord.id.in_(api.ids)))


def test_crud_persistido_y_login(api, passwords):
    response = api.register(path="/v1/users", headers=api.admin_headers)
    assert response.status_code == 201, response.text
    user = response.json()
    detail = f"/v1/users/{user['id']}"
    with SessionLocal() as session:
        record = session.get(UserRecord, user["id"])
        assert record.password_hash != PASSWORD
        assert record.password_hash.startswith("$argon2")
        assert passwords.verify(PASSWORD, record.password_hash)
    assert api.client.get(detail, headers=api.admin_headers).json() == user
    headers = api.headers(user["email"])
    assert api.client.get("/v1/users/me", headers=headers).json() == user
    assert api.client.get("/v1/users", headers=headers).status_code == 403
    # Recorre páginas para que el test también funcione con datos locales existentes.
    found = False
    offset = 0
    while not found:
        page = api.client.get(
            "/v1/users",
            params={"offset": offset, "limit": 100},
            headers=api.admin_headers,
        )
        assert page.status_code == 200
        rows = page.json()
        found = any(row["id"] == user["id"] for row in rows)
        if len(rows) < 100:
            break
        offset += 100
    assert found
    updated = api.client.put(
        detail,
        headers=headers,
        json={
            "name": "Nombre actualizado",
            "email": user["email"],
            "is_active": True,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["created_at"] == user["created_at"]
    fetched = httpx.get(
        str(api.client.base_url.join(detail)), headers=headers, timeout=10
    )
    assert fetched.json() == updated.json()
    deleted = api.client.delete(detail, headers=headers)
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert api.client.get(detail, headers=api.admin_headers).status_code == 404
    assert api.client.get("/v1/users/me", headers=headers).status_code == 401
    assert api.login(user["email"]).status_code == 401


def test_registro_normaliza_email_y_conflicto_revierte_cambios(api):
    email = f"{uuid4().hex}@example.com"
    first = api.register(f" {email.upper()} ")
    assert first.status_code == 201
    assert first.json()["email"] == email
    assert api.register(email).status_code == 409
    second = api.register().json()
    response = api.client.put(
        f"/v1/users/{second['id']}",
        headers=api.admin_headers,
        json={
            "name": "No debe persistir",
            "email": email,
            "is_active": False,
        },
    )
    assert response.status_code == 409
    assert "INSERT" not in response.text and "UPDATE" not in response.text
    assert (
        api.client.get(f"/v1/users/{second['id']}", headers=api.admin_headers).json()
        == second
    )


def test_baja_y_cambio_password_revocan_sesiones(api):
    user = api.register().json()
    old_headers = api.headers(user["email"])
    detail = f"/v1/users/{user['id']}"
    profile = {"name": user["name"], "email": user["email"], "is_active": True}
    new_password = "New-Integration-Password-6789"
    assert (
        api.client.put(
            detail, headers=old_headers, json=profile | {"password": new_password}
        ).status_code
        == 200
    )
    assert api.client.get("/v1/users/me", headers=old_headers).status_code == 401
    assert api.login(user["email"]).status_code == 401
    login = api.login(user["email"], new_password)
    assert login.status_code == 200
    new_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert api.client.get("/v1/users/me", headers=new_headers).status_code == 200
    assert (
        api.client.put(
            detail, headers=api.admin_headers, json=profile | {"is_active": False}
        ).status_code
        == 200
    )
    assert api.client.get("/v1/users/me", headers=new_headers).status_code == 401
    assert api.login(user["email"], new_password).status_code == 401


def test_no_modifica_ni_borra_usuarios_ajenos(api):
    first = api.register().json()
    second = api.register().json()
    headers = api.headers(first["email"])
    path = f"/v1/users/{second['id']}"
    assert api.client.get(path, headers=headers).status_code == 403
    assert (
        api.client.put(
            path,
            headers=headers,
            json={
                "name": "Intruso",
                "email": second["email"],
                "is_active": False,
            },
        ).status_code
        == 403
    )
    assert api.client.delete(path, headers=headers).status_code == 403
    assert api.client.get(path, headers=api.admin_headers).json() == second


def test_datos_demo_repetibles_sin_sobrescribir(api):
    credentials = {
        "DEMO_ADMIN_EMAIL": f"demo-admin-{uuid4().hex}@example.com",
        "DEMO_USER_EMAIL": f"demo-user-{uuid4().hex}@example.com",
        "DEMO_ADMIN_PASSWORD": PASSWORD,
        "DEMO_USER_PASSWORD": PASSWORD,
    }
    emails = [credentials["DEMO_ADMIN_EMAIL"], credentials["DEMO_USER_EMAIL"]]
    with SessionLocal() as session:
        assert seed_users(session, credentials) == 2
    with SessionLocal() as session:
        records = session.scalars(
            select(UserRecord).where(UserRecord.email.in_(emails))
        ).all()
        api.ids.extend(record.id for record in records)
        hashes = {record.email: record.password_hash for record in records}
    with SessionLocal() as session:
        assert seed_users(session, credentials) == 0
    with SessionLocal() as session:
        records = session.scalars(
            select(UserRecord).where(UserRecord.email.in_(emails))
        ).all()
        assert {record.email: record.password_hash for record in records} == hashes
    for email in emails:
        assert api.login(email).status_code == 200


def test_seed_no_promueve_cuentas_existentes(api):
    user = api.register().json()
    with SessionLocal() as session, pytest.raises(ValueError, match="otro rol"):
        seed_users(
            session,
            {
                "DEMO_ADMIN_EMAIL": user["email"],
                "DEMO_ADMIN_PASSWORD": PASSWORD,
                "DEMO_USER_EMAIL": f"unused-{uuid4().hex}@example.com",
                "DEMO_USER_PASSWORD": PASSWORD,
            },
        )
    with SessionLocal() as session:
        assert session.get(UserRecord, user["id"]).role == "user"


def test_registro_concurrente_con_email_unico(api):
    email = f"{uuid4().hex}@example.com"
    barrier = Barrier(2)

    def create(_):
        barrier.wait(timeout=5)
        return api.register(email)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(create, [1, 2]))
    assert sorted(response.status_code for response in results) == [201, 409]
    with SessionLocal() as session:
        assert (
            len(
                session.scalars(
                    select(UserRecord).where(UserRecord.email == email)
                ).all()
            )
            == 1
        )
