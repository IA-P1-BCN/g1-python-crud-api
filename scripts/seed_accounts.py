"""Cuentas iniciales sin reiniciar credenciales ni apropiarse de identidades."""


from email_validator import EmailNotValidError, validate_email
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.errors import ConflictError
from src.domain.security import PasswordHasher
from src.infrastructure.database.models import (
    ClienteRecord,
    CuentaRecord,
    EntrenadorRecord,
)

DEMO_PASSWORD = "Demo56789012"
ADMIN_DEMO_EMAIL = "admin.demo@gymflow.com"
ADMIN_DEMO_PASSWORD = "AdminDemo56789012"

# Una cuenta staff por entrenador demo (email -> nombre del Entrenador).
STAFF_ACCOUNTS = (
    ("staff@gymflow.com", "Laura Demo", "Yoga"),
    ("boxeo@gymflow.com", "Oscar Rivas", "Boxeo"),
    ("spinning@gymflow.com", "Nora Prieto", "Spinning"),
)


def validate_admin_password(password: str | None) -> str:
    if password is None or not 12 <= len(password) <= 128:
        raise ValueError("Configura ADMIN_PASSWORD con entre 12 y 128 caracteres")
    if password.lower().startswith(("change-me", "cambia-", "replace-")):
        raise ValueError("Sustituye el marcador de ADMIN_PASSWORD")
    return password


def seed_accounts(
    session: Session, hasher: PasswordHasher, admin_email: str, admin_password: str
) -> dict[str, int]:
    """Crea la Cuenta admin del entorno. No devuelve credenciales.

    El resto de cuentas (staff y socios demo) las crea el seed demo con
    credenciales conocidas; los clientes sin Cuenta reciben una inactiva e
    inaccesible en la migración de identidad (ADR 0002).
    """
    validate_admin_password(admin_password)
    admin_email = validate_email(
        admin_email, check_deliverability=False
    ).normalized.lower()
    admin = session.scalar(
        select(CuentaRecord).where(CuentaRecord.email == admin_email)
    )
    if admin is not None and (admin.rol != "admin" or admin.id_cliente is not None):
        raise ConflictError("ADMIN_EMAIL pertenece a otra Cuenta; usa otro email")
    counts = {"creadas": 0, "omitidas": 0}
    if admin is None:
        session.add(
            CuentaRecord(
                nombre="Administración GymFlow",
                email=admin_email,
                password_hash=hasher.hash(admin_password),
                rol="admin",
                activo=True,
            )
        )
        counts["creadas"] += 1
    else:
        counts["omitidas"] += 1
    session.flush()
    return counts


def seed_admin_demo(
    session: Session,
    hasher: PasswordHasher,
    demo_email: str = ADMIN_DEMO_EMAIL,
) -> dict[str, int]:
    """Cuenta pública de demostración; nunca modifica identidades existentes."""
    occupied_account = session.scalar(
        select(CuentaRecord).where(CuentaRecord.email == demo_email)
    )
    if occupied_account is not None:
        return {"creadas": 0, "omitidas": 1}
    session.add(
        CuentaRecord(
            nombre="Administración Demo GymFlow",
            email=demo_email,
            password_hash=hasher.hash(ADMIN_DEMO_PASSWORD),
            rol="admin",
            activo=True,
        )
    )
    session.flush()
    return {"creadas": 1, "omitidas": 0}


def seed_staff(
    session: Session,
    hasher: PasswordHasher,
    accounts: tuple[tuple[str, str, str], ...] = STAFF_ACCOUNTS,
) -> dict[str, int]:
    """Cuenta staff por entrenador demo, vinculada a su Entrenador.

    Nunca restablece credenciales ni toma vínculos ajenos: si el email ya
    existe o el Entrenador ya está vinculado, se omite esa cuenta.
    """
    counts = {"creadas": 0, "omitidas": 0}
    for staff_email, nombre_entrenador, _especialidad in accounts:
        if (
            session.scalar(
                select(CuentaRecord).where(CuentaRecord.email == staff_email)
            )
            is not None
        ):
            counts["omitidas"] += 1
            continue
        entrenador = session.scalar(
            select(EntrenadorRecord)
            .where(EntrenadorRecord.nombre == nombre_entrenador)
            .order_by(EntrenadorRecord.id_entrenador)
            .limit(1)
        )
        vinculado = (
            entrenador is not None
            and session.scalar(
                select(CuentaRecord).where(
                    CuentaRecord.id_entrenador == entrenador.id_entrenador
                )
            )
            is not None
        )
        if entrenador is None or vinculado:
            counts["omitidas"] += 1
            continue
        session.add(
            CuentaRecord(
                nombre=entrenador.nombre,
                email=staff_email,
                password_hash=hasher.hash(DEMO_PASSWORD),
                rol="staff",
                activo=True,
                id_entrenador=entrenador.id_entrenador,
            )
        )
        counts["creadas"] += 1
    session.flush()
    return counts


def cuenta_demo_socio(
    session: Session,
    hasher: PasswordHasher,
    *,
    email: str,
    nombre: str,
    estado_membresia: str,
) -> bool:
    """Crea (si falta) el par Cliente + Cuenta activa de un socio demo.

    Devuelve True si creó algo; False si ya existía la Cuenta.
    """
    try:
        email = validate_email(email, check_deliverability=False).normalized.lower()
    except EmailNotValidError:
        return False
    if (
        session.scalar(select(CuentaRecord).where(CuentaRecord.email == email))
        is not None
    ):
        return False
    cliente = ClienteRecord(estado_membresia=estado_membresia)
    session.add(cliente)
    session.flush()
    session.add(
        CuentaRecord(
            nombre=nombre,
            email=email,
            id_cliente=cliente.id_cliente,
            password_hash=hasher.hash(DEMO_PASSWORD),
            rol="cliente",
            activo=True,
        )
    )
    session.flush()
    return True
