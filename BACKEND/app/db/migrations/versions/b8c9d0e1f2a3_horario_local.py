"""horario_local

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-10-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b8c9d0e1f2a3"
down_revision: Union[str, None] = "a7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "horario_local",
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("cerrado", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("opens_at", sa.Time(), nullable=True),
        sa.Column("closes_at", sa.Time(), nullable=True),
        sa.PrimaryKeyConstraint("weekday"),
    )


def downgrade() -> None:
    op.drop_table("horario_local")
