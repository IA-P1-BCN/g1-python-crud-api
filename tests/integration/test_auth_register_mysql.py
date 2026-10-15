"""Registro por HTTP vivo y persistencia confirmada en MySQL."""

from uuid import uuid4

import httpx
import pytest
from sqlalchemy import delete, inspect, select, text
from sqlalchemy.exc import OperationalError

from src.infrastructure.database.engine import SessionLocal, engine
from src.infrastructure.database.models import ClienteRecord, CuentaRecord
from src.infrastructure.security.passwords import Argon2PasswordHasher


@pytest.fixture
def accounts_api(base_url):
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError:
        pytest.skip("MySQL no disponible: ejecuta task db:up y task migrate")
    assert inspect(engine).has_table("users"), "Aplica task migrate"
    emails = []
    with httpx.Client(base_url=base_url, timeout=10) as client:
        try:
            yield client, emails
        finally:
            with SessionLocal.begin() as session:
                session.execute(
                    delete(CuentaRecord).where(CuentaRecord.email.in_(emails))
                )
                session.execute(
                    delete(ClienteRecord).where(ClienteRecord.email.in_(emails))
                )


def test_registro_y_perfil_atomicos(accounts_api):
    client, emails = accounts_api
    email = f"{uuid4().hex}@example.com"
    emails.append(email)
    password = " contraseña sin recortar "
    payload = {
        "nombre": "Nueva socia",
        "email": email,
        "password": password,
        "crear_cliente": True,
    }
    response = client.post("/v1/auth/register", json=payload)
    assert response.status_code == 201, response.text
    assert "password" not in response.text
    with SessionLocal() as session:
        cuenta = session.get(CuentaRecord, response.json()["id"])
        assert Argon2PasswordHasher().verify(password, cuenta.password_hash)
        assert not Argon2PasswordHasher().verify(password.strip(), cuenta.password_hash)
        cliente = session.get(ClienteRecord, cuenta.id_cliente)
        assert cliente.email == email and cliente.estado_membresia == "Inactivo"
    assert client.post("/v1/auth/register", json=payload).status_code == 409


def test_no_se_apropia_de_cliente_existente(accounts_api):
    client, emails = accounts_api
    email = f"{uuid4().hex}@example.com"
    emails.append(email)
    response = client.post(
        "/v1/clientes",
        json={"nombre": "Existente", "email": email, "estado_membresia": "Activo"},
    )
    assert response.status_code == 201
    response = client.post(
        "/v1/auth/register",
        json={
            "nombre": "Otra",
            "email": email,
            "password": "contraseña segura",
            "crear_cliente": True,
        },
    )
    assert response.status_code == 409
    with SessionLocal() as session:
        assert (
            session.scalar(select(CuentaRecord).where(CuentaRecord.email == email))
            is None
        )
        assert (
            session.scalar(
                select(ClienteRecord).where(ClienteRecord.email == email)
            ).nombre
            == "Existente"
        )
