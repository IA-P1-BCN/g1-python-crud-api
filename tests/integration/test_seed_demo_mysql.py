"""El seed demo deja 3 entrenadores con clase y cuenta staff, y 22 socios (#132)."""

import pytest
from sqlalchemy import func, inspect, select, text
from sqlalchemy.exc import OperationalError

from scripts.seed_accounts import seed_staff
from scripts.seed_gym import ENTRENADORES_DEMO, SOCIOS_DEMO, seed_demo
from src.infrastructure.database.engine import SessionLocal, engine
from src.infrastructure.database.models import (
    ClaseRecord,
    CuentaRecord,
    EntrenadorRecord,
)
from src.infrastructure.security.passwords import Argon2PasswordHasher

pytestmark = pytest.mark.order(-1)


@pytest.fixture(scope="module", autouse=True)
def _sembrado():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError:
        pytest.skip("MySQL no disponible: ejecuta task db:up y task migrate")
    assert inspect(engine).has_table("users"), "Aplica task migrate"
    hasher = Argon2PasswordHasher()
    with SessionLocal.begin() as session:
        seed_demo(session, hasher)
        seed_staff(session, hasher)


def test_hay_tres_entrenadores_con_clase_y_staff():
    with SessionLocal() as session:
        for nombre, _especialidad, nombre_clase, _hora in ENTRENADORES_DEMO:
            entrenador = session.scalar(
                select(EntrenadorRecord).where(EntrenadorRecord.nombre == nombre)
            )
            assert entrenador is not None, f"Falta el entrenador {nombre}"
            clase = session.scalar(
                select(ClaseRecord).where(ClaseRecord.nombre_clase == nombre_clase)
            )
            assert clase is not None and clase.id_entrenador == entrenador.id_entrenador
            cuenta = session.scalar(
                select(CuentaRecord).where(
                    CuentaRecord.id_entrenador == entrenador.id_entrenador
                )
            )
            assert cuenta is not None and cuenta.rol == "staff" and cuenta.activo


def test_hay_veintidos_socios_demo_activos():
    with SessionLocal() as session:
        total = session.scalar(
            select(func.count())
            .select_from(CuentaRecord)
            .where(CuentaRecord.email.like("socio%@gymflow.com"))
        )
        assert total == len(SOCIOS_DEMO) == 22


def test_seed_es_idempotente():
    hasher = Argon2PasswordHasher()
    with SessionLocal.begin() as session:
        seed_demo(session, hasher)
        seed_staff(session, hasher)
    with SessionLocal() as session:
        total = session.scalar(
            select(func.count())
            .select_from(CuentaRecord)
            .where(CuentaRecord.email.like("socio%@gymflow.com"))
        )
        assert total == 22
