"""vincula cuenta staff con entrenador

Revision ID: 7a0f6a730e04
Revises: ca6c9ed6b7e8
Create Date: 2026-10-16 11:52:45.843110

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7a0f6a730e04"
down_revision: str | None = "ca6c9ed6b7e8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("id_entrenador", sa.Integer(), nullable=True))
    op.create_unique_constraint("uq_users_id_entrenador", "users", ["id_entrenador"])
    op.create_foreign_key(
        "fk_users_id_entrenador",
        "users",
        "entrenadores",
        ["id_entrenador"],
        ["id_entrenador"],
        ondelete="RESTRICT",
    )
    versions = sa.table("versions", sa.column("version", sa.String(20)))
    op.bulk_insert(versions, [{"version": "0.4"}])


def downgrade() -> None:
    versions = sa.table("versions", sa.column("version", sa.String(20)))
    op.execute(versions.delete().where(versions.c.version == "0.4"))
    op.drop_constraint("fk_users_id_entrenador", "users", type_="foreignkey")
    op.drop_constraint("uq_users_id_entrenador", "users", type_="unique")
    op.drop_column("users", "id_entrenador")
