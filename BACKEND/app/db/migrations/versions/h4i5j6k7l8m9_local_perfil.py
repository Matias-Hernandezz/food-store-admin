"""local_perfil

Revision ID: h4i5j6k7l8m9
Revises: g3b4c5d6e7f8
Create Date: 2026-10-23

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "h4i5j6k7l8m9"
down_revision: Union[str, None] = "g3b4c5d6e7f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "local_perfil",
        sa.Column("id", sa.Integer(), primary_key=True, server_default="1"),
        sa.Column("nombre_negocio", sa.String(120), nullable=False, server_default="Food Store"),
        sa.Column("telefono", sa.String(40), nullable=True),
        sa.Column("email_contacto", sa.String(150), nullable=True),
        sa.Column("direccion", sa.String(250), nullable=True),
        sa.Column("ciudad", sa.String(100), nullable=True),
        sa.Column("whatsapp", sa.String(40), nullable=True),
    )
    op.execute(
        "INSERT INTO local_perfil (id, nombre_negocio) VALUES (1, 'Food Store') "
        "ON CONFLICT (id) DO NOTHING"
    )


def downgrade() -> None:
    op.drop_table("local_perfil")
