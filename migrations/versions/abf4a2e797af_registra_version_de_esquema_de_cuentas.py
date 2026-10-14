"""registra version de esquema de cuentas

Revision ID: abf4a2e797af
Revises: f42402d59e55
Create Date: 2026-10-14 14:34:20.376230

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "abf4a2e797af"
down_revision: str | None = "f42402d59e55"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    versions = sa.table("versions", sa.column("version", sa.String(20)))
    op.bulk_insert(versions, [{"version": "0.3"}])


def downgrade() -> None:
    versions = sa.table("versions", sa.column("version", sa.String(20)))
    op.execute(versions.delete().where(versions.c.version == "0.3"))
