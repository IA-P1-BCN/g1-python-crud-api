"""crea cuentas separadas de clientes

Revision ID: f42402d59e55
Revises: 2ffa1c174fb4
Create Date: 2026-10-14 13:43:46.684502

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f42402d59e55"
down_revision: str | None = "2ffa1c174fb4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("email", sa.String(150), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("activo", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("rol", sa.String(20), server_default="cliente", nullable=False),
        sa.Column("id_cliente", sa.Integer(), nullable=True),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("id_cliente", name="uq_users_id_cliente"),
        sa.CheckConstraint("rol IN ('admin', 'staff', 'cliente')", name="ck_users_rol"),
        sa.ForeignKeyConstraint(
            ["id_cliente"],
            ["clientes.id_cliente"],
            name="fk_users_cliente",
            ondelete="RESTRICT",
        ),
    )


def downgrade() -> None:
    op.drop_table("users")
