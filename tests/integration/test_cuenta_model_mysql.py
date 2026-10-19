"""Restricciones MySQL y seed dentro de una transacción reversible."""

from uuid import uuid4

import pytest
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError, OperationalError

from scripts.seed_accounts import seed_accounts
from src.infrastructure.database.engine import SessionLocal, engine
from src.infrastructure.database.models import (
    ClienteRecord,
    CuentaRecord,
    VersionRecord,
)
from src.infrastructure.security.passwords import Argon2PasswordHasher


@pytest.fixture
def account_session():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError:
        pytest.skip("MySQL no disponible: ejecuta task db:up y task migrate")
    assert inspect(engine).has_table("users"), "Aplica task migrate"
    with SessionLocal() as session:
        try:
            yield session
        finally:
            session.rollback()


def test_migracion_unicidad_y_vinculo(account_session):
    session = account_session
    assert (
        session.scalar(select(VersionRecord).where(VersionRecord.version == "0.3"))
        is not None
    )
    cliente = ClienteRecord(estado_membresia="Activo")
    session.add(cliente)
    session.flush()
    email = f"{uuid4().hex}@example.com"
    cuenta = CuentaRecord(
        nombre="Prueba",
        email=email,
        password_hash="hash",
        id_cliente=cliente.id_cliente,
    )
    session.add(cuenta)
    session.flush()
    assert cuenta.activo and cuenta.rol == "cliente"
    assert cuenta.fecha_creacion is not None
    for data in [
        {"email": email},
        {"email": f"{uuid4().hex}@example.com", "id_cliente": cliente.id_cliente},
        {"email": f"{uuid4().hex}@example.com", "rol": "root"},
    ]:
        with (
            pytest.raises((IntegrityError, OperationalError)) as error,
            session.begin_nested(),
        ):
            session.add(CuentaRecord(nombre="Duplicada", password_hash="hash", **data))
            session.flush()
        assert error.value.orig.args[0] == (3819 if "rol" in data else 1062)
    with pytest.raises(IntegrityError), session.begin_nested():
        session.delete(cliente)
        session.flush()
    session.delete(cuenta)
    session.flush()
    assert session.get(ClienteRecord, cliente.id_cliente) is not None


def test_seed_no_duplica_ni_modifica_cuentas(account_session):
    session = account_session
    member = ClienteRecord(estado_membresia="Suspendido")
    session.add(member)
    session.flush()
    admin_email = f"{uuid4().hex}@example.com"
    password = "contraseña admin de prueba"
    hasher = Argon2PasswordHasher()
    seed_accounts(session, hasher, admin_email, password)
    admin = session.scalar(
        select(CuentaRecord).where(CuentaRecord.email == admin_email)
    )
    assert hasher.verify(password, admin.password_hash)
    assert admin.rol == "admin" and admin.activo and admin.id_cliente is None
    # Las cuentas de socios las crea el seed demo; el cliente queda intacto.
    assert (
        session.scalar(
            select(CuentaRecord).where(CuentaRecord.id_cliente == member.id_cliente)
        )
        is None
    )
    assert member.estado_membresia == "Suspendido"
    previous = {r.id: r.password_hash for r in session.scalars(select(CuentaRecord))}
    assert (
        seed_accounts(session, hasher, admin_email, "otra contraseña segura")["creadas"]
        == 0
    )
    assert {
        r.id: r.password_hash for r in session.scalars(select(CuentaRecord))
    } == previous
