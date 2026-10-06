"""Crea dos cuentas de demostración, sin modificar usuarios existentes."""

import os
from datetime import UTC, datetime
from pathlib import Path
from secrets import token_urlsafe

from dotenv import dotenv_values
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.database.models import UserRecord
from src.infrastructure.security.auth import Argon2Passwords


def demo_credentials(path: Path = Path(".env.demo")) -> dict[str, str]:
    if not path.exists():
        contents = (
            "DEMO_ADMIN_EMAIL=admin.demo@example.com\n"
            f"DEMO_ADMIN_PASSWORD={token_urlsafe(24)}\n"
            "DEMO_USER_EMAIL=user.demo@example.com\n"
            f"DEMO_USER_PASSWORD={token_urlsafe(24)}\n"
        )
        with open(
            path, "x", opener=lambda name, flags: os.open(name, flags, 0o600)
        ) as file:
            file.write(contents)
    values = dotenv_values(path)
    required = [
        f"DEMO_{role}_{field}"
        for role in ("ADMIN", "USER")
        for field in ("EMAIL", "PASSWORD")
    ]
    if any(not values.get(key) for key in required):
        raise ValueError("Faltan credenciales en .env.demo")
    if any(len(values[key]) < 12 for key in required if key.endswith("PASSWORD")):
        raise ValueError("Las contraseñas de demo deben tener al menos 12 caracteres")
    path.chmod(0o600)
    return {key: values[key] for key in required}


def seed_users(session: Session, credentials: dict[str, str]) -> int:
    passwords = Argon2Passwords()
    created = 0
    with session.begin():
        for role, name in [("admin", "Administrador demo"), ("user", "Usuario demo")]:
            email = credentials[f"DEMO_{role.upper()}_EMAIL"].strip().lower()
            existing = session.scalar(
                select(UserRecord).where(UserRecord.email == email)
            )
            if existing is not None:
                if existing.role != role:
                    raise ValueError(
                        "Ya existe una cuenta con ese email y otro rol; no se modifica"
                    )
                continue
            session.add(
                UserRecord(
                    name=name,
                    email=email,
                    role=role,
                    is_active=True,
                    token_version=0,
                    password_hash=passwords.hash(
                        credentials[f"DEMO_{role.upper()}_PASSWORD"]
                    ),
                    created_at=datetime.now(UTC).replace(tzinfo=None),
                )
            )
            created += 1
    return created


def main() -> None:
    from src.infrastructure.database.engine import SessionLocal

    credentials = demo_credentials()
    with SessionLocal() as session:
        created = seed_users(session, credentials)
    print(
        f"Demo preparada: {created} cuentas creadas. Credenciales locales en .env.demo."
    )


if __name__ == "__main__":
    main()
