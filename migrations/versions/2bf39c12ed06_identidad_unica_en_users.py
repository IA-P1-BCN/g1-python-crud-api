"""identidad única en users: clientes pierde nombre y email

Revision ID: 2bf39c12ed06
Revises: 7a0f6a730e04
Create Date: 2026-10-19

Cada cliente sin Cuenta recibe una Cuenta inactiva con su identidad y un
hash de un secreto aleatorio descartado (no puede iniciar sesión). Después,
la identidad solo vive en users (ADR 0002).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2bf39c12ed06"
down_revision: str | None = "7a0f6a730e04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Hash Argon2id de un secreto aleatorio descartado: ninguna contraseña lo verifica.
HASH_SIN_LOGIN = "$argon2id$v=19$m=65536,t=3,p=4$2C7j3nQKqVGMK6K9E6E/MQ$tPswZZPFlWVu5ALIvt0q5CLJ0H86Jxs1RUqW7o0jcXY"


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            INSERT INTO users
                (nombre, email, password_hash, activo, rol, id_cliente, fecha_creacion)
            SELECT
                c.nombre,
                CASE
                    WHEN c.email IS NULL OR c.email = ''
                      OR EXISTS (SELECT 1 FROM users u2 WHERE u2.email = c.email)
                    THEN CONCAT('cliente-', c.id_cliente, '@demo.local')
                    ELSE c.email
                END,
                :hash_sin_login,
                0,
                'cliente',
                c.id_cliente,
                NOW()
            FROM clientes c
            LEFT JOIN users u ON u.id_cliente = c.id_cliente
            WHERE u.id IS NULL
            """
        ).bindparams(hash_sin_login=HASH_SIN_LOGIN)
    )
    op.drop_constraint("uq_clientes_email", "clientes", type_="unique")
    op.drop_column("clientes", "nombre")
    op.drop_column("clientes", "email")
    versions = sa.table("versions", sa.column("version", sa.String(20)))
    op.bulk_insert(versions, [{"version": "0.5"}])


def downgrade() -> None:
    versions = sa.table("versions", sa.column("version", sa.String(20)))
    op.execute(versions.delete().where(versions.c.version == "0.5"))
    op.add_column("clientes", sa.Column("nombre", sa.String(100), nullable=True))
    op.add_column("clientes", sa.Column("email", sa.String(150), nullable=True))
    op.execute(
        sa.text(
            """
            UPDATE clientes c
            LEFT JOIN users u ON u.id_cliente = c.id_cliente
            SET c.nombre = u.nombre, c.email = u.email
            """
        )
    )
    op.create_unique_constraint("uq_clientes_email", "clientes", ["email"])
