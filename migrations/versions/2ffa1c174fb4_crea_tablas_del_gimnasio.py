"""crea tablas del gimnasio

Revision ID: 2ffa1c174fb4
Revises: 0001
Create Date: 2026-10-06 11:57:41.501018

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2ffa1c174fb4"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "clientes",
        sa.Column("id_cliente", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("email", sa.String(150), nullable=True),
        sa.Column("fecha_inscripcion", sa.Date(), nullable=True),
        sa.Column("estado_membresia", sa.String(20), nullable=False),
        sa.UniqueConstraint("email", name="uq_clientes_email"),
        sa.CheckConstraint(
            "estado_membresia IN ('Activo', 'Inactivo', 'Suspendido')",
            name="ck_clientes_estado_membresia",
        ),
    )
    op.create_table(
        "entrenadores",
        sa.Column("id_entrenador", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("especialidad", sa.String(100), nullable=True),
        sa.Column("telefono", sa.String(20), nullable=True),
    )
    op.create_table(
        "clases",
        sa.Column("id_clase", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nombre_clase", sa.String(50), nullable=False),
        sa.Column("horario", sa.DateTime(), nullable=False),
        sa.Column("capacidad_max", sa.Integer(), nullable=False),
        sa.Column(
            "id_entrenador",
            sa.Integer(),
            sa.ForeignKey("entrenadores.id_entrenador", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.CheckConstraint("capacidad_max > 0", name="ck_clases_capacidad_max"),
    )
    op.create_index("ix_clases_id_entrenador", "clases", ["id_entrenador"])
    op.create_table(
        "reservas",
        sa.Column("id_reserva", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "id_cliente",
            sa.Integer(),
            sa.ForeignKey("clientes.id_cliente", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "id_clase",
            sa.Integer(),
            sa.ForeignKey("clases.id_clase", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "fecha_reserva", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("asistio", sa.Boolean(), nullable=False, server_default="0"),
        sa.UniqueConstraint("id_cliente", "id_clase", name="uq_reservas_cliente_clase"),
    )
    op.create_index("ix_reservas_id_cliente", "reservas", ["id_cliente"])
    op.create_index("ix_reservas_id_clase", "reservas", ["id_clase"])
    op.create_table(
        "pagos",
        sa.Column("id_pago", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "id_cliente",
            sa.Integer(),
            sa.ForeignKey("clientes.id_cliente", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("monto", sa.Numeric(10, 2), nullable=False),
        sa.Column("fecha_pago", sa.Date(), nullable=False),
        sa.Column("metodo_pago", sa.String(30), nullable=True),
        sa.CheckConstraint("monto > 0", name="ck_pagos_monto"),
        sa.CheckConstraint(
            "metodo_pago IN ('Tarjeta', 'Transferencia', 'Efectivo')",
            name="ck_pagos_metodo_pago",
        ),
    )
    op.create_index("ix_pagos_id_cliente", "pagos", ["id_cliente"])
    versions = sa.table("versions", sa.column("version", sa.String(20)))
    op.bulk_insert(versions, [{"version": "0.2"}])


def downgrade() -> None:
    op.drop_table("pagos")
    op.drop_table("reservas")
    op.drop_table("clases")
    op.drop_table("entrenadores")
    op.drop_table("clientes")
    versions = sa.table("versions", sa.column("version", sa.String(20)))
    op.execute(versions.delete().where(versions.c.version == "0.2"))
