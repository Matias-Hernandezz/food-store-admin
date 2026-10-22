"""tenant mercado pago credentials

Revision ID: g2b3c4d5e6f7
Revises: f1a2b3c4d5e6
Create Date: 2026-10-21

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "g2b3c4d5e6f7"
down_revision: Union[str, None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tenants",
        sa.Column("mp_access_token", sa.String(length=512), nullable=True),
    )
    op.add_column(
        "tenants",
        sa.Column("mp_webhook_secret", sa.String(length=256), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tenants", "mp_webhook_secret")
    op.drop_column("tenants", "mp_access_token")
