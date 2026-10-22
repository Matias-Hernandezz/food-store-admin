"""tenant delivery_app_fee_percent

Revision ID: i5d6e7f8a9b0
Revises: h4c5d6e7f8a9
Create Date: 2026-10-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "i5d6e7f8a9b0"
down_revision: Union[str, None] = "h4c5d6e7f8a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tenants",
        sa.Column(
            "delivery_app_fee_percent",
            sa.Numeric(5, 2),
            nullable=False,
            server_default="30.00",
        ),
    )


def downgrade() -> None:
    op.drop_column("tenants", "delivery_app_fee_percent")
