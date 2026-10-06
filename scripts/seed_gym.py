"""Datos ficticios de GymFlow: ejecutar después de `task migrate`."""

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.database.engine import SessionLocal
from src.infrastructure.database.models import (
    ClaseRecord,
    ClienteRecord,
    EntrenadorRecord,
    PagoRecord,
    ReservaRecord,
)


def seed_demo(session: Session) -> None:
    """Añade registros ausentes; el llamador controla la transacción.

    Los emails y nombres Demo identifican estos datos. Una segunda ejecución
    conserva las ediciones hechas a los registros que ya existen.
    """
    session.flush()
    clientes = []
    for nombre, email, estado in [
        ("Ana Demo", "ana.demo@example.com", "Activo"),
        ("Bruno Demo", "bruno.demo@example.com", "Inactivo"),
        ("Carla Demo", "carla.demo@example.com", "Suspendido"),
    ]:
        cliente = session.scalar(
            select(ClienteRecord).where(ClienteRecord.email == email)
        )
        if cliente is None:
            cliente = ClienteRecord(
                nombre=nombre,
                email=email,
                estado_membresia=estado,
                fecha_inscripcion=date(2026, 10, 1),
            )
            session.add(cliente)
            session.flush()
        clientes.append(cliente)

    entrenador = session.scalar(
        select(EntrenadorRecord)
        .where(EntrenadorRecord.nombre == "Laura Demo")
        .order_by(EntrenadorRecord.id_entrenador)
        .limit(1)
    )
    if entrenador is None:
        entrenador = EntrenadorRecord(
            nombre="Laura Demo", especialidad="Yoga", telefono=None
        )
        session.add(entrenador)
        session.flush()

    clase = session.scalar(
        select(ClaseRecord)
        .where(ClaseRecord.nombre_clase == "Yoga Demo")
        .order_by(ClaseRecord.id_clase)
        .limit(1)
    )
    if clase is None:
        clase = ClaseRecord(
            nombre_clase="Yoga Demo",
            horario=datetime(2026, 11, 1, 10, tzinfo=UTC).replace(tzinfo=None),
            capacidad_max=10,
            id_entrenador=entrenador.id_entrenador,
        )
        session.add(clase)
        session.flush()

    ana = clientes[0]
    pago = session.scalar(
        select(PagoRecord).where(PagoRecord.id_cliente == ana.id_cliente).limit(1)
    )
    if pago is None:
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
    session.refresh(ana, with_for_update=True)
    session.refresh(clase, with_for_update=True)
    reservas = list(
        session.scalars(
            select(ReservaRecord)
            .where(ReservaRecord.id_clase == clase.id_clase)
            .with_for_update()
        )
    )
    tiene_reserva = any(reserva.id_cliente == ana.id_cliente for reserva in reservas)
    if (
        not tiene_reserva
        and ana.estado_membresia == "Activo"
        and len(reservas) < clase.capacidad_max
    ):
        session.add(
            ReservaRecord(
                id_cliente=ana.id_cliente,
                id_clase=clase.id_clase,
                fecha_reserva=datetime(2026, 10, 6, 10, tzinfo=UTC).replace(
                    tzinfo=None
                ),
                asistio=False,
            )
        )
    session.flush()


def main() -> None:
    with SessionLocal.begin() as session:
        seed_demo(session)
    print(
        "Datos demo de GymFlow disponibles: clientes, entrenador, clase, pago y reserva."
    )


if __name__ == "__main__":
    main()
