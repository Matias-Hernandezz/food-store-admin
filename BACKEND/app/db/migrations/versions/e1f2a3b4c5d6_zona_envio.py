"""zona_envio

Revision ID: e1f2a3b4c5d6
Revises: c9d0e1f2a3b4
Create Date: 2026-10-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, None] = "c9d0e1f2a3b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "zona_envio",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(80), nullable=False),
        sa.Column("ciudad_match", sa.String(120), nullable=True),
        sa.Column("costo_envio", sa.Numeric(10, 2), nullable=False, server_default="50.00"),
        sa.Column("pedido_minimo", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("activa", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("orden", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(
        """
        INSERT INTO zona_envio (nombre, ciudad_match, costo_envio, pedido_minimo, activa, orden)
        VALUES ('General', NULL, 50.00, 0.00, true, 0)
        """
    )


def downgrade() -> None:
    op.drop_table("zona_envio")
