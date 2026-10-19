"""Registro por HTTP vivo y persistencia confirmada en MySQL."""

from uuid import uuid4

from sqlalchemy import select

from src.infrastructure.database.engine import SessionLocal
from src.infrastructure.database.models import ClienteRecord, CuentaRecord
from src.infrastructure.security.passwords import Argon2PasswordHasher


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
        assert cliente.estado_membresia == "Inactivo"
        assert cuenta.email == email
    assert client.post("/v1/auth/register", json=payload).status_code == 409


def test_registro_nunca_vincula_cliente_existente(accounts_api, gym_admin_headers):
    """Con la identidad en users (ADR 0002), el registro crea su propio Cliente."""
    client, emails = accounts_api
    email = f"{uuid4().hex}@example.com"
    emails.append(email)
    response = client.post(
        "/v1/clientes",
        headers=gym_admin_headers,
        json={"estado_membresia": "Activo"},
    )
    assert response.status_code == 201
    previo = response.json()["id_cliente"]
    response = client.post(
        "/v1/auth/register",
        json={
            "nombre": "Otra",
            "email": email,
            "password": "contraseña segura",
            "crear_cliente": True,
        },
    )
    assert response.status_code == 201, response.text
    with SessionLocal() as session:
        cuenta = session.scalar(
            select(CuentaRecord).where(CuentaRecord.email == email)
        )
        assert cuenta is not None and cuenta.id_cliente is not None
        assert cuenta.id_cliente != previo
        previo_record = session.get(ClienteRecord, previo)
        assert previo_record is not None and previo_record.estado_membresia == "Activo"
