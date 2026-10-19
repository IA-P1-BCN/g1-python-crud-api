"""Datos ficticios de GymFlow: ejecutar después de `task migrate`."""

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from config.settings import get_settings
from scripts.seed_accounts import (
    DEMO_PASSWORD,
    cuenta_demo_socio,
    seed_accounts,
    seed_admin_demo,
    seed_staff,
    validate_admin_password,
)
from src.infrastructure.database.engine import SessionLocal
from src.infrastructure.database.models import (
    ClaseRecord,
    ClienteRecord,
    CuentaRecord,
    EntrenadorRecord,
    PagoRecord,
    ReservaRecord,
)
from src.infrastructure.security.passwords import Argon2PasswordHasher

# (nombre del entrenador, especialidad, nombre de su clase, hora)
ENTRENADORES_DEMO = (
    ("Laura Demo", "Yoga", "Yoga Demo", 10),
    ("Oscar Rivas", "Boxeo", "Boxeo Iniciación", 18),
    ("Nora Prieto", "Spinning", "Spinning Express", 19),
)

# 22 socios demo: la mayoría activos, algunos inactivos y suspendidos.
SOCIOS_DEMO = (
    ("Sofía Rey", "Activo"),
    ("Mateo Gil", "Activo"),
    ("Lucía Navas", "Activo"),
    ("Hugo Vidal", "Activo"),
    ("Martina Cano", "Activo"),
    ("Leo Prats", "Activo"),
    ("Valeria Soler", "Activo"),
    ("Daniel Ortiz", "Activo"),
    ("Alma Rivas", "Activo"),
    ("Iker Mora", "Activo"),
    ("Nerea Peña", "Activo"),
    ("Adrián Lago", "Activo"),
    ("Carla Duarte", "Activo"),
    ("Pau Ferrer", "Activo"),
    ("Iris Sáez", "Activo"),
    ("Nico Bravo", "Activo"),
    ("Elena Cortés", "Activo"),
    ("Marc Puig", "Activo"),
    ("Aitana Vera", "Inactivo"),
    ("Bruno Nieto", "Inactivo"),
    ("Vera Román", "Suspendido"),
    ("Omar Leal", "Suspendido"),
)

EMAIL_SOCIO = "socio{:02d}@gymflow.com"


def _cliente_por_cuenta(session: Session, email: str) -> ClienteRecord | None:
    """Localiza un cliente demo por el email de su Cuenta vinculada."""
    cuenta = session.scalar(select(CuentaRecord).where(CuentaRecord.email == email))
    if cuenta is None or cuenta.id_cliente is None:
        return None
    return session.get(ClienteRecord, cuenta.id_cliente)


def seed_demo(session: Session, hasher: Argon2PasswordHasher) -> None:
    """Añade registros ausentes; el llamador controla la transacción.

    Una segunda ejecución conserva las ediciones y credenciales existentes.
    """
    session.flush()

    # Clientes históricos del demo V1, identificados por la Cuenta vinculada.
    for email, estado in [
        ("ana.demo@example.com", "Activo"),
        ("bruno.demo@example.com", "Inactivo"),
        ("carla.demo@example.com", "Suspendido"),
    ]:
        if _cliente_por_cuenta(session, email) is None:
            cliente = ClienteRecord(
                estado_membresia=estado,
                fecha_inscripcion=date(2026, 10, 1),
            )
            session.add(cliente)
            session.flush()
            session.add(
                CuentaRecord(
                    nombre=email.split("@")[0].title() + " Demo",
                    email=email,
                    id_cliente=cliente.id_cliente,
                    password_hash=hasher.hash(DEMO_PASSWORD),
                    rol="cliente",
                    activo=False,
                )
            )
            session.flush()

    # Tres entrenadores con su clase: Yoga, Boxeo y Spinning.
    clases: dict[str, ClaseRecord] = {}
    for nombre, especialidad, nombre_clase, hora in ENTRENADORES_DEMO:
        entrenador = session.scalar(
            select(EntrenadorRecord)
            .where(EntrenadorRecord.nombre == nombre)
            .order_by(EntrenadorRecord.id_entrenador)
            .limit(1)
        )
        if entrenador is None:
            entrenador = EntrenadorRecord(
                nombre=nombre, especialidad=especialidad, telefono=None
            )
            session.add(entrenador)
            session.flush()
        clase = session.scalar(
            select(ClaseRecord)
            .where(ClaseRecord.nombre_clase == nombre_clase)
            .order_by(ClaseRecord.id_clase)
            .limit(1)
        )
        if clase is None:
            clase = ClaseRecord(
                nombre_clase=nombre_clase,
                horario=datetime(2026, 11, 1, hora, tzinfo=UTC).replace(tzinfo=None),
                capacidad_max=10,
                id_entrenador=entrenador.id_entrenador,
            )
            session.add(clase)
            session.flush()
        clases[nombre_clase] = clase

    # 22 socios demo con Cuenta activa y contraseña conocida.
    for indice, (nombre, estado) in enumerate(SOCIOS_DEMO, start=1):
        cuenta_demo_socio(
            session,
            hasher,
            email=EMAIL_SOCIO.format(indice),
            nombre=nombre,
            estado_membresia=estado,
        )

    ana = _cliente_por_cuenta(session, "ana.demo@example.com")
    clase_yoga = clases["Yoga Demo"]
    pago = (
        session.scalar(
            select(PagoRecord).where(PagoRecord.id_cliente == ana.id_cliente).limit(1)
        )
        if ana is not None
        else None
    )
    if ana is not None and pago is None:
        session.add(
            PagoRecord(
                id_cliente=ana.id_cliente,
                monto=Decimal("35.00"),
                fecha_pago=date(2026, 10, 1),
                metodo_pago="Tarjeta",
            )
        )
        session.flush()

    # El seed también respeta admisión y aforo si se modificaron los datos demo.
    if ana is None or ana.estado_membresia != "Activo":
        session.flush()
        return
    session.refresh(ana, with_for_update=True)
    session.refresh(clase_yoga, with_for_update=True)
    reservas = list(
        session.scalars(
            select(ReservaRecord)
            .where(ReservaRecord.id_clase == clase_yoga.id_clase)
            .with_for_update()
        )
    )
    tiene_reserva = any(reserva.id_cliente == ana.id_cliente for reserva in reservas)
    if not tiene_reserva and len(reservas) < clase_yoga.capacidad_max:
        session.add(
            ReservaRecord(
                id_cliente=ana.id_cliente,
                id_clase=clase_yoga.id_clase,
                fecha_reserva=datetime(2026, 10, 6, 10, tzinfo=UTC).replace(
                    tzinfo=None
                ),
                asistio=False,
            )
        )
    session.flush()


def main() -> None:
    settings = get_settings()
    password = validate_admin_password(
        settings.admin_password.get_secret_value() if settings.admin_password else None
    )
    hasher = Argon2PasswordHasher()
    with SessionLocal.begin() as session:
        seed_demo(session, hasher)
        counts = seed_accounts(
            session, hasher, settings.admin_email, password
        )
        staff = seed_staff(session, hasher)
        admin_demo = seed_admin_demo(session, hasher)
        total_entrenadores = len(
            list(session.scalars(select(EntrenadorRecord.id_entrenador)))
        )
        total_socios = (
            session.query(CuentaRecord)
            .filter(CuentaRecord.email.like("socio%@gymflow.com"))
            .count()
        )
    print("Datos demo: 3 entrenadores (Boxeo/Yoga/Spinning) con clase y cuenta staff.")
    print(f"Socios demo activos con contraseña demo: {total_socios}/22.")
    print(f"Entrenadores totales: {total_entrenadores}.")
    print(f"Cuenta admin del entorno: {counts['creadas']} creadas; {counts['omitidas']} omitidas.")
    if admin_demo["creadas"]:
        print("Cuenta admin demo creada: admin.demo@gymflow.com (credenciales en README).")
    else:
        print("Cuenta admin demo omitida: ya existía.")
    print(
        f"Cuentas staff: {staff['creadas']} creadas; {staff['omitidas']} omitidas "
        "(staff@, boxeo@, spinning@gymflow.com)."
    )


if __name__ == "__main__":
    main()
