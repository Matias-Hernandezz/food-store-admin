"""tenant mp oauth fields

Revision ID: h4c5d6e7f8a9
Revises: g2b3c4d5e6f7
Create Date: 2026-10-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "h4c5d6e7f8a9"
down_revision: Union[str, None] = "g2b3c4d5e6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "tenants",
        "mp_access_token",
        existing_type=sa.String(length=512),
        type_=sa.String(length=2048),
        existing_nullable=True,
    )
    op.add_column("tenants", sa.Column("mp_refresh_token", sa.String(length=2048), nullable=True))
    op.add_column("tenants", sa.Column("mp_public_key", sa.String(length=128), nullable=True))
    op.add_column("tenants", sa.Column("mp_user_id", sa.String(length=64), nullable=True))
    op.add_column("tenants", sa.Column("mp_token_expires_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("tenants", "mp_token_expires_at")
    op.drop_column("tenants", "mp_user_id")
    op.drop_column("tenants", "mp_public_key")
    op.drop_column("tenants", "mp_refresh_token")
    op.alter_column(
        "tenants",
        "mp_access_token",
        existing_type=sa.String(length=2048),
        type_=sa.String(length=512),
        existing_nullable=True,
    )
