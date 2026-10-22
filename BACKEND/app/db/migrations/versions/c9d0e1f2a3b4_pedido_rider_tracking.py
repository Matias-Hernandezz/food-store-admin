"""pedido rider tracking

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-10-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c9d0e1f2a3b4"
down_revision: Union[str, None] = "b8c9d0e1f2a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("pedido", sa.Column("rider_token", sa.String(64), nullable=True))
    op.add_column("pedido", sa.Column("rider_lat", sa.Float(), nullable=True))
    op.add_column("pedido", sa.Column("rider_lng", sa.Float(), nullable=True))
    op.add_column("pedido", sa.Column("rider_location_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_pedido_rider_token", "pedido", ["rider_token"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_pedido_rider_token", table_name="pedido")
    op.drop_column("pedido", "rider_location_at")
    op.drop_column("pedido", "rider_lng")
    op.drop_column("pedido", "rider_lat")
    op.drop_column("pedido", "rider_token")
