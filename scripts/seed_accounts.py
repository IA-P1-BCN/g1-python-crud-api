"""Cuentas iniciales sin reiniciar credenciales ni apropiarse de identidades."""

from secrets import token_urlsafe

from email_validator import EmailNotValidError, validate_email
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.domain.errors import ConflictError
from src.domain.security import PasswordHasher
from src.infrastructure.database.models import (
    ClienteRecord,
    CuentaRecord,
    EntrenadorRecord,
)

STAFF_EMAIL = "staff@gymflow.com"
DEMO_PASSWORD = "Demo56789012"
ADMIN_DEMO_EMAIL = "admin.demo@gymflow.com"
ADMIN_DEMO_PASSWORD = "AdminDemo56789012"


def validate_admin_password(password: str | None) -> str:
    if password is None or not 12 <= len(password) <= 128:
        raise ValueError("Configura ADMIN_PASSWORD con entre 12 y 128 caracteres")
    if password.lower().startswith(("change-me", "cambia-", "replace-")):
        raise ValueError("Sustituye el marcador de ADMIN_PASSWORD")
    return password


def seed_accounts(
    session: Session, hasher: PasswordHasher, admin_email: str, admin_password: str
) -> dict[str, int]:
    """El llamador controla la transacción. No devuelve credenciales."""
    validate_admin_password(admin_password)
    admin_email = validate_email(
        admin_email, check_deliverability=False
    ).normalized.lower()
    admin = session.scalar(
        select(CuentaRecord).where(CuentaRecord.email == admin_email)
    )
    if admin is not None and (admin.rol != "admin" or admin.id_cliente is not None):
        raise ConflictError("ADMIN_EMAIL pertenece a otra Cuenta; usa otro email")
    if (
        session.scalar(select(ClienteRecord).where(ClienteRecord.email == admin_email))
        is not None
    ):
        raise ConflictError("ADMIN_EMAIL pertenece a un Cliente; usa otro email")
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
    session.flush()
    for cliente in session.scalars(select(ClienteRecord)):
        try:
            email = validate_email(
                cliente.email or "", check_deliverability=False
            ).normalized.lower()
        except EmailNotValidError:
            counts["omitidas"] += 1
            continue
        existing = session.scalar(
            select(CuentaRecord).where(
                or_(
                    CuentaRecord.id_cliente == cliente.id_cliente,
                    CuentaRecord.email == email,
                )
            )
        )
        if existing is not None:
            counts["omitidas"] += 1
            continue
        session.add(
            CuentaRecord(
                nombre=cliente.nombre,
                email=email,
                id_cliente=cliente.id_cliente,
                password_hash=hasher.hash(token_urlsafe(32)),
                rol="cliente",
                activo=False,
            )
        )
        session.flush()
        counts["creadas"] += 1
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
    occupied_client = session.scalar(
        select(ClienteRecord).where(ClienteRecord.email == demo_email)
    )
    if occupied_account is not None or occupied_client is not None:
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
    session: Session, hasher: PasswordHasher, staff_email: str = STAFF_EMAIL
) -> dict[str, int]:
    """Crea la Cuenta staff demo vinculada a un Entrenador, si es posible.

    El llamador controla la transacción. No restablece credenciales ni toma
    vínculos ajenos: si el email ya existe u no hay Entrenador libre, se omite.
    """
    counts = {"creadas": 0, "omitidas": 0}
    if (
        session.scalar(select(CuentaRecord).where(CuentaRecord.email == staff_email))
        is not None
    ):
        counts["omitidas"] += 1
        return counts
    vinculados = select(CuentaRecord.id_entrenador).where(
        CuentaRecord.id_entrenador.is_not(None)
    )
    entrenador = session.scalar(
        select(EntrenadorRecord)
        .where(~EntrenadorRecord.id_entrenador.in_(vinculados))
        .order_by(EntrenadorRecord.id_entrenador)
        .limit(1)
    )
    if entrenador is None:
        counts["omitidas"] += 1
        return counts
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
    session.flush()
    counts["creadas"] += 1
    return counts
