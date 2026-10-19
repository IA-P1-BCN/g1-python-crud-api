"""Alta conjunta Entrenador+Cuenta staff contra MySQL real (#134)."""

from uuid import uuid4

import httpx
import pytest
from sqlalchemy import func, select

from src.infrastructure.database.engine import SessionLocal
from src.infrastructure.database.models import CuentaRecord, EntrenadorRecord
from src.infrastructure.security.passwords import Argon2PasswordHasher


@pytest.fixture
def cuentas_api(accounts_api, gym_admin_headers):
    client, emails = accounts_api
    return client, emails, {"Authorization": gym_admin_headers["Authorization"]}


def _limpiar(email: str) -> None:
    with SessionLocal.begin() as session:
        cuenta = session.scalar(
            select(CuentaRecord).where(CuentaRecord.email == email)
        )
        if cuenta is not None:
            entrenador = (
                session.get(EntrenadorRecord, cuenta.id_entrenador)
                if cuenta.id_entrenador is not None
                else None
            )
            session.delete(cuenta)
            session.flush()
            if entrenador is not None:
                session.delete(entrenador)


def test_alta_con_email_crea_cuenta_staff_y_login(cuentas_api, base_url):
    client, emails, admin = cuentas_api
    email = f"staff-{uuid4().hex}@gymflow.com"
    emails.append(email)
    try:
        respuesta = client.post(
            "/v1/entrenadores",
            headers=admin,
            json={"nombre": "Entrenador Alta", "especialidad": "Boxeo", "email": email},
        )
        assert respuesta.status_code == 201, respuesta.text
        cuerpo = respuesta.json()
        assert cuerpo["email"] == email
        assert cuerpo["id_user"] is not None
        with SessionLocal() as session:
            cuenta = session.scalar(
                select(CuentaRecord).where(CuentaRecord.email == email)
            )
            assert cuenta.rol == "staff" and cuenta.activo
            assert cuenta.id_entrenador == cuerpo["id_entrenador"]
            assert Argon2PasswordHasher().verify("Demo56789012", cuenta.password_hash)
        with httpx.Client(base_url=base_url, timeout=10) as publico:
            login = publico.post(
                "/v1/auth/login",
                data={"username": email, "password": "Demo56789012"},
            )
            assert login.status_code == 200, login.text
    finally:
        _limpiar(email)


def test_email_duplicado_409_y_rollback_del_entrenador(cuentas_api):
    client, emails, admin = cuentas_api
    email = f"staff-{uuid4().hex}@gymflow.com"
    emails.append(email)
    try:
        primero = client.post(
            "/v1/entrenadores",
            headers=admin,
            json={"nombre": "Primero", "email": email},
        )
        assert primero.status_code == 201
        with SessionLocal() as session:
            total = session.scalar(
                select(func.count()).select_from(EntrenadorRecord)
            )
        duplicado = client.post(
            "/v1/entrenadores",
            headers=admin,
            json={"nombre": "Segundo", "email": email},
        )
        assert duplicado.status_code == 409
        with SessionLocal() as session:
            assert (
                session.scalar(
                    select(func.count()).select_from(EntrenadorRecord)
                )
                == total
            ), "El rollback debe dejar el Entrenador sin crear"
    finally:
        _limpiar(email)


def test_staff_no_puede_crear_entrenadores(cuentas_api):
    client, emails, admin = cuentas_api
    email = f"staff-{uuid4().hex}@gymflow.com"
    emails.append(email)
    try:
        alta = client.post(
            "/v1/entrenadores",
            headers=admin,
            json={"nombre": "Creado por admin", "email": email},
        )
        assert alta.status_code == 201
        login = client.post(
            "/v1/auth/login",
            data={"username": email, "password": "Demo56789012"},
        )
        staff = {"Authorization": f"Bearer {login.json()['access_token']}"}
        respuesta = client.post(
            "/v1/entrenadores",
            headers=staff,
            json={"nombre": "Intruso", "email": "intruso@gymflow.com"},
        )
        assert respuesta.status_code == 403
        sin_token = client.post("/v1/entrenadores", json={"nombre": "Anónimo"})
        assert sin_token.status_code == 401
    finally:
        _limpiar(email)
