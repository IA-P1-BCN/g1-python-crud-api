"""Seed de Cuentas demo de roles: idempotencia, vínculo y logins."""

from uuid import uuid4

import httpx
import pytest
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import OperationalError

from config.settings import get_settings
from scripts.seed_accounts import (
    DEMO_PASSWORD,
    STAFF_EMAIL,
    seed_accounts,
    seed_staff,
)
from src.infrastructure.database.engine import SessionLocal, engine
from src.infrastructure.database.models import (
    CuentaRecord,
    EntrenadorRecord,
)
from src.infrastructure.security.passwords import Argon2PasswordHasher


@pytest.fixture
def seed_session():
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


def _entrenador_libre(session):
    vinculados = select(CuentaRecord.id_entrenador).where(
        CuentaRecord.id_entrenador.is_not(None)
    )
    return session.scalar(
        select(EntrenadorRecord)
        .where(~EntrenadorRecord.id_entrenador.in_(vinculados))
        .order_by(EntrenadorRecord.id_entrenador)
        .limit(1)
    )


def _hashes(session):
    return {
        record.id: record.password_hash
        for record in session.scalars(select(CuentaRecord))
    }


def test_seed_staff_crea_vinculo_y_es_idempotente(seed_session):
    session = seed_session
    hasher = Argon2PasswordHasher()
    if _entrenador_libre(session) is None:
        session.add(
            EntrenadorRecord(nombre=f"Entrenador {uuid4().hex[:8]}", especialidad="Yoga")
        )
        session.flush()
    email = f"staff-{uuid4().hex}@example.com"
    primera = seed_staff(session, hasher, staff_email=email)
    assert primera == {"creadas": 1, "omitidas": 0}
    cuenta = session.scalar(select(CuentaRecord).where(CuentaRecord.email == email))
    assert cuenta.rol == "staff" and cuenta.activo
    assert cuenta.id_cliente is None
    assert cuenta.id_entrenador is not None
    assert hasher.verify(DEMO_PASSWORD, cuenta.password_hash)
    entrenador = session.get(EntrenadorRecord, cuenta.id_entrenador)
    assert entrenador is not None
    assert entrenador.nombre
    antes = _hashes(session)
    segunda = seed_staff(session, hasher, staff_email=email)
    assert segunda == {"creadas": 0, "omitidas": 1}
    assert _hashes(session) == antes
    assert (
        session.scalar(select(CuentaRecord).where(CuentaRecord.email == email))
    ).id_entrenador == entrenador.id_entrenador


def test_seed_staff_email_ocupado_no_modifica(seed_session):
    session = seed_session
    hasher = Argon2PasswordHasher()
    email = f"staff-{uuid4().hex}@example.com"
    propia = CuentaRecord(
        nombre="Cuenta ajena",
        email=email,
        password_hash=hasher.hash("otra contraseña segura"),
        rol="cliente",
        activo=True,
    )
    session.add(propia)
    session.flush()
    resultado = seed_staff(session, hasher, staff_email=email)
    assert resultado == {"creadas": 0, "omitidas": 1}
    intacta = session.scalar(select(CuentaRecord).where(CuentaRecord.email == email))
    assert intacta.rol == "cliente" and intacta.id_entrenador is None
    assert hasher.verify("otra contraseña segura", intacta.password_hash)


def test_seed_staff_sin_entrenador_libre_se_omite(seed_session):
    session = seed_session
    hasher = Argon2PasswordHasher()
    if _entrenador_libre(session) is None:
        session.add(
            EntrenadorRecord(
                nombre=f"Entrenador {uuid4().hex[:8]}", especialidad="Yoga"
            )
        )
        session.flush()
    for entrenador in session.scalars(select(EntrenadorRecord)):
        vinculado = session.scalar(
            select(CuentaRecord).where(
                CuentaRecord.id_entrenador == entrenador.id_entrenador
            )
        )
        if vinculado is None:
            session.add(
                CuentaRecord(
                    nombre=entrenador.nombre,
                    email=f"vinculo-{uuid4().hex}@example.com",
                    password_hash=hasher.hash("otra contraseña segura"),
                    rol="staff",
                    activo=True,
                    id_entrenador=entrenador.id_entrenador,
                )
            )
    session.flush()
    assert _entrenador_libre(session) is None
    email = f"staff-{uuid4().hex}@example.com"
    resultado = seed_staff(session, hasher, staff_email=email)
    assert resultado == {"creadas": 0, "omitidas": 1}
    assert (
        session.scalar(select(CuentaRecord).where(CuentaRecord.email == email)) is None
    )


def _password_admin():
    ajustes = get_settings()
    valor = (
        ajustes.admin_password.get_secret_value() if ajustes.admin_password else None
    )
    if valor is not None and 12 <= len(valor) <= 128:
        return valor, ajustes.admin_email
    return DEMO_PASSWORD, ajustes.admin_email


def test_login_cuentas_demo(base_url):
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError:
        pytest.skip("MySQL no disponible: ejecuta task db:up y task migrate")
    assert inspect(engine).has_table("users"), "Aplica task migrate"
    hasher = Argon2PasswordHasher()
    password_admin, admin_email = _password_admin()
    creadas: list[str] = []
    entrenador_propio = False
    try:
        with SessionLocal.begin() as session:
            demo = session.scalar(
                select(CuentaRecord).where(CuentaRecord.email == "demo@gymflow.com")
            )
            if demo is None or not demo.activo:
                pytest.skip("Falta la cuenta demo: aplica task migrate")
            if (
                session.scalar(
                    select(CuentaRecord).where(CuentaRecord.email == STAFF_EMAIL)
                )
                is None
            ):
                if _entrenador_libre(session) is None:
                    session.add(
                        EntrenadorRecord(
                            nombre=f"Entrenador {uuid4().hex[:8]}",
                            especialidad="Yoga",
                        )
                    )
                    session.flush()
                    entrenador_propio = True
                assert seed_staff(session, hasher)["creadas"] == 1
                creadas.append(STAFF_EMAIL)
            if (
                session.scalar(
                    select(CuentaRecord).where(CuentaRecord.email == admin_email)
                )
                is None
            ):
                seed_accounts(session, hasher, admin_email, password_admin)
                creadas.append(admin_email)
        with httpx.Client(base_url=base_url, timeout=10) as client:
            for email, password in (
                (admin_email, password_admin),
                (STAFF_EMAIL, DEMO_PASSWORD),
                ("demo@gymflow.com", DEMO_PASSWORD),
            ):
                respuesta = client.post(
                    "/v1/auth/login", data={"username": email, "password": password}
                )
                assert respuesta.status_code == 200, respuesta.text
                assert respuesta.json()["access_token"]
    finally:
        if creadas or entrenador_propio:
            with SessionLocal.begin() as session:
                staff = session.scalar(
                    select(CuentaRecord).where(
                        CuentaRecord.email.in_(creadas),
                        CuentaRecord.rol == "staff",
                    )
                )
                for email in creadas:
                    cuenta = session.scalar(
                        select(CuentaRecord).where(CuentaRecord.email == email)
                    )
                    if cuenta is not None:
                        session.delete(cuenta)
                session.flush()
                if entrenador_propio and (
                    staff is not None
                    and session.get(EntrenadorRecord, staff.id_entrenador) is not None
                ):
                    vinculo = session.scalar(
                        select(CuentaRecord).where(
                            CuentaRecord.id_entrenador == staff.id_entrenador
                        )
                    )
                    if vinculo is None:
                        session.delete(
                            session.get(EntrenadorRecord, staff.id_entrenador)
                        )
