"""pedido tracking_token

Revision ID: a7b8c9d0e1f2
Revises: e5a1c2d3f4b6
Create Date: 2026-10-21 21:15:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, None] = "e5a1c2d3f4b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    import secrets

    op.add_column(
        "pedido",
        sa.Column("tracking_token", sa.String(length=64), nullable=True),
    )
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id FROM pedido WHERE tracking_token IS NULL"))
    for row in rows:
        token = secrets.token_urlsafe(32)
        conn.execute(
            sa.text("UPDATE pedido SET tracking_token = :t WHERE id = :id"),
            {"t": token, "id": row.id},
        )
    op.alter_column("pedido", "tracking_token", nullable=False)
    op.create_index(op.f("ix_pedido_tracking_token"), "pedido", ["tracking_token"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_pedido_tracking_token"), table_name="pedido")
    op.drop_column("pedido", "tracking_token")
