"""detalle_pedido_surrogate_pk

Revision ID: c3308d83eb84
Revises: 6fb82597aa76
Create Date: 2026-06-29 22:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = 'c3308d83eb84'
down_revision: Union[str, None] = '6fb82597aa76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Agregar columna id como SERIAL (autoincremental, nullable al principio)
    op.execute("ALTER TABLE detalle_pedido ADD COLUMN id SERIAL")

    # 2. Eliminar la PK compuesta (pedido_id, producto_id)
    op.drop_constraint('detalle_pedido_pkey', 'detalle_pedido', type_='primary')

    # 3. Establecer id como nueva PK
    op.create_primary_key('detalle_pedido_pkey', 'detalle_pedido', ['id'])

    # 4. Agregar índices para los FKs
    op.create_index('ix_detalle_pedido_pedido_id', 'detalle_pedido', ['pedido_id'])
    op.create_index('ix_detalle_pedido_producto_id', 'detalle_pedido', ['producto_id'])


def downgrade() -> None:
    op.drop_index('ix_detalle_pedido_producto_id', table_name='detalle_pedido')
    op.drop_index('ix_detalle_pedido_pedido_id', table_name='detalle_pedido')
    op.drop_constraint('detalle_pedido_pkey', 'detalle_pedido', type_='primary')
    op.drop_column('detalle_pedido', 'id')
    op.create_primary_key('detalle_pedido_pkey', 'detalle_pedido', ['pedido_id', 'producto_id'])
