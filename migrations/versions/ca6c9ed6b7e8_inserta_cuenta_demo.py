"""inserta cuenta demo

Revision ID: ca6c9ed6b7e8
Revises: abf4a2e797af
Create Date: 2026-10-16 10:32:13.372007

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "ca6c9ed6b7e8"
down_revision: str | None = "abf4a2e797af"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

EMAIL = "demo@gymflow.com"
PASSWORD_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=4$V06tVnTz4P2Aw11ZeQVeMA$"
    "/07IqZNIP98pc0OFtKcBl3uQWP0e/RACaOxy/G4OgVk"
)


def upgrade() -> None:
    conn = op.get_bind()
    if conn.execute(
        sa.text("SELECT id FROM users WHERE email = :email"),
        {"email": EMAIL},
    ).first():
        return
    conn.execute(
        sa.text(
            "INSERT INTO clientes (nombre, email, fecha_inscripcion, estado_membresia) "
            "VALUES ('Demo GymFlow', :email, CURRENT_DATE, 'Activo')"
        ),
        {"email": EMAIL},
    )
    cliente_id = conn.execute(sa.text("SELECT LAST_INSERT_ID()")).scalar()
    conn.execute(
        sa.text(
            "INSERT INTO pagos (id_cliente, monto, fecha_pago, metodo_pago) "
            "VALUES (:id_cliente, 30.00, CURRENT_DATE, 'Efectivo')"
        ),
        {"id_cliente": cliente_id},
    )
    conn.execute(
        sa.text(
            "INSERT INTO users "
            "(nombre, email, password_hash, activo, rol, id_cliente) "
            "VALUES ('Demo GymFlow', :email, :password_hash, 1, 'cliente', :id_cliente)"
        ),
        {
            "email": EMAIL,
            "password_hash": PASSWORD_HASH,
            "id_cliente": cliente_id,
        },
    )


def downgrade() -> None:
    conn = op.get_bind()
    row = conn.execute(
        sa.text(
            "SELECT id_cliente FROM users "
            "WHERE email = :email AND password_hash = :password_hash"
        ),
        {"email": EMAIL, "password_hash": PASSWORD_HASH},
    ).first()
    if row is None:
        return
    conn.execute(
        sa.text(
            "DELETE FROM users WHERE email = :email AND password_hash = :password_hash"
        ),
        {"email": EMAIL, "password_hash": PASSWORD_HASH},
    )
    if row.id_cliente is None:
        return
    conn.execute(
        sa.text("DELETE FROM reservas WHERE id_cliente = :id_cliente"),
        {"id_cliente": row.id_cliente},
    )
    conn.execute(
        sa.text("DELETE FROM pagos WHERE id_cliente = :id_cliente"),
        {"id_cliente": row.id_cliente},
    )
    conn.execute(
        sa.text(
            "DELETE FROM clientes WHERE id_cliente = :id_cliente AND email = :email"
        ),
        {"id_cliente": row.id_cliente, "email": EMAIL},
    )
