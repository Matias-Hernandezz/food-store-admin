"""config_fiscal + comprobante_fiscal

Revision ID: g3b4c5d6e7f8
Revises: f2a3b4c5d6e7
Create Date: 2026-10-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "g3b4c5d6e7f8"
down_revision: Union[str, None] = "f2a3b4c5d6e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "config_fiscal",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cuit", sa.String(11), nullable=False, server_default="00000000000"),
        sa.Column("razon_social", sa.String(120), nullable=False, server_default="Local"),
        sa.Column("punto_venta", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("condicion_iva", sa.String(20), nullable=False, server_default="MONOTRIBUTO"),
        sa.Column("adapter", sa.String(32), nullable=False, server_default="mock"),
        sa.Column("habilitado", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(
        """
        INSERT INTO config_fiscal (cuit, razon_social, punto_venta, condicion_iva, adapter, habilitado)
        VALUES ('00000000000', 'Local demo', 1, 'MONOTRIBUTO', 'mock', false)
        """
    )

    op.create_table(
        "comprobante_fiscal",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pedido_id", sa.Integer(), sa.ForeignKey("pedido.id"), nullable=False),
        sa.Column("tipo_comprobante", sa.Integer(), nullable=False, server_default="11"),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("cae", sa.String(14), nullable=True),
        sa.Column("cae_vencimiento", sa.Date(), nullable=True),
        sa.Column("estado", sa.String(20), nullable=False, server_default="PENDIENTE_CAE"),
        sa.Column("importe_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("qr_payload", sa.Text(), nullable=True),
        sa.Column("error_detalle", sa.Text(), nullable=True),
        sa.Column("idempotency_key", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pedido_id"),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index("ix_comprobante_fiscal_pedido_id", "comprobante_fiscal", ["pedido_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_comprobante_fiscal_pedido_id", table_name="comprobante_fiscal")
    op.drop_table("comprobante_fiscal")
    op.drop_table("config_fiscal")
