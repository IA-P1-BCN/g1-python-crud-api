"""crea la tabla versions y siembra la versión 0.1

Revision ID: 0001
Revises:
Create Date: 2026-10-05

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

versions_table = sa.table(
    "versions",
    sa.column("version", sa.String(length=20)),
)


def upgrade() -> None:
    op.create_table(
        "versions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("version", sa.String(length=20), nullable=False),
        sa.Column(
            "applied_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("version", name="uq_versions_version"),
    )
    op.bulk_insert(versions_table, [{"version": "0.1"}])


def downgrade() -> None:
    op.drop_table("versions")
