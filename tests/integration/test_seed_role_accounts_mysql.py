"""Seed de Cuentas demo de roles: idempotencia, vínculo y logins."""

from uuid import uuid4

import httpx
import pytest
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import OperationalError

from config.settings import get_settings
from scripts.seed_accounts import (
    ADMIN_DEMO_PASSWORD,
    DEMO_PASSWORD,
    seed_accounts,
    seed_admin_demo,
    seed_staff,
)
from src.infrastructure.database.engine import SessionLocal, engine
from src.infrastructure.database.models import (
    ClienteRecord,
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
            EntrenadorRecord(
                nombre=f"Entrenador {uuid4().hex[:8]}", especialidad="Yoga"
            )
        )
        session.flush()
    entrenador = _entrenador_libre(session)
    email = f"staff-{uuid4().hex}@example.com"
    cuenta_cuenta = ((email, entrenador.nombre, "Yoga"),)
    primera = seed_staff(session, hasher, accounts=cuenta_cuenta)
    assert primera == {"creadas": 1, "omitidas": 0}
    cuenta = session.scalar(select(CuentaRecord).where(CuentaRecord.email == email))
    assert cuenta.rol == "staff" and cuenta.activo
    assert cuenta.id_cliente is None
    assert cuenta.id_entrenador == entrenador.id_entrenador
    assert hasher.verify(DEMO_PASSWORD, cuenta.password_hash)
    antes = _hashes(session)
    segunda = seed_staff(session, hasher, accounts=cuenta_cuenta)
    assert segunda == {"creadas": 0, "omitidas": 1}
    assert _hashes(session) == antes
    assert (
        session.scalar(select(CuentaRecord).where(CuentaRecord.email == email))
    ).id_entrenador == entrenador.id_entrenador


def test_admin_demo_argon2_y_repeticion_conserva_ediciones(seed_session):
    session = seed_session
    hasher = Argon2PasswordHasher()
    email = f"admin-demo-{uuid4().hex}@example.com"
    assert seed_admin_demo(session, hasher, email) == {"creadas": 1, "omitidas": 0}
    cuenta = session.scalar(select(CuentaRecord).where(CuentaRecord.email == email))
    assert cuenta.rol == "admin" and cuenta.activo
    assert cuenta.id_cliente is None and cuenta.id_entrenador is None
    assert cuenta.password_hash.startswith("$argon2id$")
    assert hasher.verify(ADMIN_DEMO_PASSWORD, cuenta.password_hash)
    cuenta.activo = False
    cuenta.rol = "cliente"
    cuenta.password_hash = hasher.hash("otra contraseña de prueba")
    session.flush()
    previous = _hashes(session)
    assert seed_admin_demo(session, hasher, email) == {"creadas": 0, "omitidas": 1}
    session.refresh(cuenta)
    assert not cuenta.activo and cuenta.rol == "cliente"
    assert _hashes(session) == previous


def test_admin_demo_no_se_apropia_de_email(seed_session):
    session = seed_session
    hasher = Argon2PasswordHasher()
    email = f"ocupado-{uuid4().hex}@example.com"
    cliente = ClienteRecord(estado_membresia="Inactivo")
    session.add(cliente)
    session.flush()
    cuenta = CuentaRecord(
        nombre="Titular",
        email=email,
        rol="cliente",
        activo=False,
        id_cliente=cliente.id_cliente,
        password_hash=hasher.hash("otra contraseña de prueba"),
    )
    session.add(cuenta)
    session.flush()
    previous = _hashes(session)
    assert seed_admin_demo(session, hasher, email) == {"creadas": 0, "omitidas": 1}
    assert _hashes(session) == previous
    session.refresh(cuenta)
    assert cuenta.rol == "cliente" and not cuenta.activo
    assert cuenta.id_cliente == cliente.id_cliente
    session.refresh(cliente)
    assert cliente.estado_membresia == "Inactivo"


def test_admin_demo_login_y_listado_admin(seed_session, base_url):
    email = f"admin-login-{uuid4().hex}@example.com"
    seed_admin_demo(seed_session, Argon2PasswordHasher(), email)
    seed_session.commit()
    try:
        with httpx.Client(base_url=base_url, timeout=10) as client:
            response = client.post(
                "/v1/auth/login",
                data={"username": email, "password": ADMIN_DEMO_PASSWORD},
            )
            assert response.status_code == 200
            headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
            profile = client.get("/v1/users/me", headers=headers)
            assert profile.status_code == 200
            assert profile.json()["rol"] == "admin"
            assert "password_hash" not in profile.text
            assert client.get("/v1/users", headers=headers).status_code == 200
    finally:
        seed_session.rollback()
        cuenta = seed_session.scalar(
            select(CuentaRecord).where(CuentaRecord.email == email)
        )
        seed_session.delete(cuenta)
        seed_session.commit()


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
    resultado = seed_staff(session, hasher, accounts=((email, "Laura Demo", "Yoga"),))
    assert resultado == {"creadas": 0, "omitidas": 1}
    intacta = session.scalar(select(CuentaRecord).where(CuentaRecord.email == email))
    assert intacta.rol == "cliente" and intacta.id_entrenador is None
    assert hasher.verify("otra contraseña segura", intacta.password_hash)


def test_seed_staff_entrenador_ya_vinculado_se_omite(seed_session):
    """Auto-suficiente: crea su propio entrenador ya vinculado por otra cuenta."""
    session = seed_session
    hasher = Argon2PasswordHasher()
    nombre = f"Entrenador {uuid4().hex[:8]}"
    session.add(EntrenadorRecord(nombre=nombre, especialidad="Yoga"))
    session.flush()
    entrenador = session.scalar(
        select(EntrenadorRecord).where(EntrenadorRecord.nombre == nombre)
    )
    session.add(
        CuentaRecord(
            nombre=nombre,
            email=f"vinculo-{uuid4().hex}@example.com",
            password_hash=hasher.hash("otra contraseña segura"),
            rol="staff",
            activo=True,
            id_entrenador=entrenador.id_entrenador,
        )
    )
    session.flush()
    email = f"staff-{uuid4().hex}@example.com"
    resultado = seed_staff(session, hasher, accounts=((email, nombre, "Yoga"),))
    assert resultado == {"creadas": 0, "omitidas": 1}
    assert (
        session.scalar(select(CuentaRecord).where(CuentaRecord.email == email)) is None
    )


def _password_admin():
    ajustes = get_settings()
    # El seed conserva claves existentes: no asumir que ADMIN_PASSWORD actual
    # coincide con la de un admin persistido en ejecuciones anteriores.
    email = f"admin-test-{uuid4().hex}@example.com"
    valor = (
        ajustes.admin_password.get_secret_value() if ajustes.admin_password else None
    )
    if valor is not None and 12 <= len(valor) <= 128:
        return valor, email
    return DEMO_PASSWORD, email


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
                    select(CuentaRecord).where(
                        CuentaRecord.email == "staff@gymflow.com"
                    )
                )
                is None
            ):
                laura = session.scalar(
                    select(EntrenadorRecord).where(
                        EntrenadorRecord.nombre == "Laura Demo"
                    )
                )
                if laura is None:
                    laura = EntrenadorRecord(nombre="Laura Demo", especialidad="Yoga")
                    session.add(laura)
                    session.flush()
                    entrenador_propio = True
                assert (
                    seed_staff(
                        session,
                        hasher,
                        accounts=(("staff@gymflow.com", "Laura Demo", "Yoga"),),
                    )["creadas"]
                    == 1
                )
                creadas.append("staff@gymflow.com")
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
                ("staff@gymflow.com", DEMO_PASSWORD),
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
