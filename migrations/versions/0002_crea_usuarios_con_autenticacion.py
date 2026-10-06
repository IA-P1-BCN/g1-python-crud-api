"""crea usuarios con autenticacion

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-06 14:19:05.078889

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("is_active", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("role", sa.String(10), server_default="user", nullable=False),
        sa.Column("token_version", sa.Integer(), server_default="0", nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.CheckConstraint("role IN ('user', 'admin')", name="ck_users_role"),
        sa.CheckConstraint("token_version >= 0", name="ck_users_token_version"),
    )
    versions = sa.table("versions", sa.column("version", sa.String(20)))
    op.bulk_insert(versions, [{"version": "0.2"}])


def downgrade() -> None:
    op.drop_table("users")
    versions = sa.table("versions", sa.column("version", sa.String(20)))
    op.execute(versions.delete().where(versions.c.version == "0.2"))
