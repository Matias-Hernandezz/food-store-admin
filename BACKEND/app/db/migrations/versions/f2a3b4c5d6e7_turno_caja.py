"""turno_caja + pedido.turno_caja_id

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6
Create Date: 2026-10-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f2a3b4c5d6e7"
down_revision: Union[str, None] = "e1f2a3b4c5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "turno_caja",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="OPEN"),
        sa.Column("abierto_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cerrado_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("usuario_apertura_id", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("usuario_cierre_id", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=True),
        sa.Column("fondo_inicial", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("efectivo_esperado", sa.Numeric(12, 2), nullable=True),
        sa.Column("efectivo_contado", sa.Numeric(12, 2), nullable=True),
        sa.Column("notas_cierre", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_turno_caja_estado", "turno_caja", ["estado"])
    op.add_column("pedido", sa.Column("turno_caja_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_pedido_turno_caja",
        "pedido",
        "turno_caja",
        ["turno_caja_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_pedido_turno_caja", "pedido", type_="foreignkey")
    op.drop_column("pedido", "turno_caja_id")
    op.drop_index("ix_turno_caja_estado", table_name="turno_caja")
    op.drop_table("turno_caja")
