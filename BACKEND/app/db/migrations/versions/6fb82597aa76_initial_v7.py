"""initial_v7

Revision ID: 6fb82597aa76
Revises: 
Create Date: 2026-06-16 18:04:22.236190

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6fb82597aa76'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all Food Store v7 tables."""
    # ── Catálogos ───────────────────────────────────────────────────────

    op.create_table(
        'rol',
        sa.Column('codigo', sa.String(20), nullable=False),
        sa.Column('nombre', sa.String(50), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('codigo'),
        sa.UniqueConstraint('nombre'),
    )

    op.create_table(
        'estado_pedido',
        sa.Column('codigo', sa.String(20), nullable=False),
        sa.Column('descripcion', sa.String(80), nullable=False),
        sa.Column('orden', sa.Integer(), nullable=False),
        sa.Column('es_terminal', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.PrimaryKeyConstraint('codigo'),
    )

    op.create_table(
        'forma_pago',
        sa.Column('codigo', sa.String(20), nullable=False),
        sa.Column('descripcion', sa.String(80), nullable=False),
        sa.Column('habilitado', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('codigo'),
    )

    op.create_table(
        'unidad_medida',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('nombre', sa.String(50), nullable=False),
        sa.Column('simbolo', sa.String(10), nullable=False),
        sa.Column('tipo', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre'),
        sa.UniqueConstraint('simbolo'),
    )

    # ── Usuarios ────────────────────────────────────────────────────────

    op.create_table(
        'usuario',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('nombre', sa.String(80), nullable=False),
        sa.Column('apellido', sa.String(80), nullable=False),
        sa.Column('email', sa.String(254), nullable=False),
        sa.Column('celular', sa.String(20), nullable=True),
        sa.Column('password_hash', sa.CHAR(60), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )

    op.create_table(
        'usuario_rol',
        sa.Column('usuario_id', sa.BigInteger(), nullable=False),
        sa.Column('rol_codigo', sa.String(20), nullable=False),
        sa.Column('asignado_por_id', sa.BigInteger(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ),
        sa.ForeignKeyConstraint(['rol_codigo'], ['rol.codigo'], ),
        sa.ForeignKeyConstraint(['asignado_por_id'], ['usuario.id'], ),
        sa.PrimaryKeyConstraint('usuario_id', 'rol_codigo'),
    )

    op.create_table(
        'refresh_token',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('usuario_id', sa.BigInteger(), nullable=False),
        sa.Column('token_hash', sa.CHAR(64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash'),
    )

    op.create_table(
        'direccion_entrega',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('usuario_id', sa.BigInteger(), nullable=False),
        sa.Column('alias', sa.String(50), nullable=True),
        sa.Column('linea1', sa.String(), nullable=False),
        sa.Column('linea2', sa.String(), nullable=True),
        sa.Column('ciudad', sa.String(100), nullable=False),
        sa.Column('provincia', sa.String(100), nullable=True),
        sa.Column('codigo_postal', sa.String(10), nullable=True),
        sa.Column('latitud', sa.Numeric(9, 6), nullable=True),
        sa.Column('longitud', sa.Numeric(9, 6), nullable=True),
        sa.Column('es_principal', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── Catálogo de productos ───────────────────────────────────────────

    op.create_table(
        'categoria',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('parent_id', sa.BigInteger(), nullable=True),
        sa.Column('nombre', sa.String(100), nullable=False),
        sa.Column('descripcion', sa.String(250), nullable=True),
        sa.Column('imagen_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['categoria.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre'),
    )

    op.create_table(
        'ingrediente',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('nombre', sa.String(100), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('es_alergeno', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('stock_cantidad', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre'),
    )

    op.create_table(
        'producto',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('nombre', sa.String(150), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('precio_base', sa.Numeric(10, 2), nullable=False),
        sa.Column('imagenes_url', postgresql.ARRAY(sa.Text()), server_default=sa.text("'{}'::text[]")),
        sa.Column('stock_cantidad', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('disponible', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('unidad_venta_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('precio_base >= 0', name='check_precio_positivo'),
        sa.CheckConstraint('stock_cantidad >= 0', name='check_stock_positivo'),
        sa.ForeignKeyConstraint(['unidad_venta_id'], ['unidad_medida.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre'),
    )

    op.create_table(
        'producto_categoria',
        sa.Column('producto_id', sa.BigInteger(), nullable=False),
        sa.Column('categoria_id', sa.BigInteger(), nullable=False),
        sa.Column('es_principal', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['producto_id'], ['producto.id'], ),
        sa.ForeignKeyConstraint(['categoria_id'], ['categoria.id'], ),
        sa.PrimaryKeyConstraint('producto_id', 'categoria_id'),
    )

    op.create_table(
        'producto_ingrediente',
        sa.Column('producto_id', sa.BigInteger(), nullable=False),
        sa.Column('ingrediente_id', sa.BigInteger(), nullable=False),
        sa.Column('es_removible', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('cantidad', sa.Numeric(10, 3), nullable=False, server_default=sa.text('1.0')),
        sa.Column('unidad_medida_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['producto_id'], ['producto.id'], ),
        sa.ForeignKeyConstraint(['ingrediente_id'], ['ingrediente.id'], ),
        sa.ForeignKeyConstraint(['unidad_medida_id'], ['unidad_medida.id'], ),
        sa.PrimaryKeyConstraint('producto_id', 'ingrediente_id'),
    )

    # ── Pedidos ─────────────────────────────────────────────────────────

    op.create_table(
        'pedido',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('usuario_id', sa.BigInteger(), nullable=False),
        sa.Column('direccion_id', sa.BigInteger(), nullable=True),
        sa.Column('estado_codigo', sa.String(20), nullable=False, server_default=sa.text("'PENDIENTE'")),
        sa.Column('forma_pago_codigo', sa.String(20), nullable=False),
        sa.Column('subtotal', sa.Numeric(10, 2), nullable=False),
        sa.Column('descuento', sa.Numeric(10, 2), nullable=False, server_default=sa.text('0.00')),
        sa.Column('costo_envio', sa.Numeric(10, 2), nullable=False, server_default=sa.text('50.00')),
        sa.Column('total', sa.Numeric(10, 2), nullable=False),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ),
        sa.ForeignKeyConstraint(['direccion_id'], ['direccion_entrega.id'], ),
        sa.ForeignKeyConstraint(['estado_codigo'], ['estado_pedido.codigo'], ),
        sa.ForeignKeyConstraint(['forma_pago_codigo'], ['forma_pago.codigo'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'detalle_pedido',
        sa.Column('pedido_id', sa.BigInteger(), nullable=False),
        sa.Column('producto_id', sa.BigInteger(), nullable=False),
        sa.Column('cantidad', sa.Integer(), nullable=False),
        sa.Column('nombre_snapshot', sa.String(200), nullable=False),
        sa.Column('precio_snapshot', sa.Numeric(10, 2), nullable=False),
        sa.Column('subtotal', sa.Numeric(10, 2), nullable=False),
        sa.Column('personalizacion', postgresql.ARRAY(sa.Integer()), server_default=sa.text("'{}'::integer[]")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['pedido_id'], ['pedido.id'], ),
        sa.ForeignKeyConstraint(['producto_id'], ['producto.id'], ),
        sa.PrimaryKeyConstraint('pedido_id', 'producto_id'),
    )

    op.create_table(
        'historial_estado_pedido',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('pedido_id', sa.BigInteger(), nullable=False),
        sa.Column('estado_desde', sa.String(20), nullable=True),
        sa.Column('estado_hacia', sa.String(20), nullable=False),
        sa.Column('usuario_id', sa.BigInteger(), nullable=True),
        sa.Column('motivo', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['pedido_id'], ['pedido.id'], ),
        sa.ForeignKeyConstraint(['estado_desde'], ['estado_pedido.codigo'], ),
        sa.ForeignKeyConstraint(['estado_hacia'], ['estado_pedido.codigo'], ),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── Pagos ───────────────────────────────────────────────────────────

    op.create_table(
        'pago',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('pedido_id', sa.BigInteger(), nullable=False),
        sa.Column('mp_payment_id', sa.BigInteger(), nullable=True),
        sa.Column('mp_status', sa.String(30), nullable=False, server_default=sa.text("'pending'")),
        sa.Column('mp_status_detail', sa.String(100), nullable=True),
        sa.Column('transaction_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('payment_method_id', sa.String(50), nullable=True),
        sa.Column('external_reference', sa.String(100), nullable=False),
        sa.Column('idempotency_key', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['pedido_id'], ['pedido.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('mp_payment_id'),
        sa.UniqueConstraint('external_reference'),
        sa.UniqueConstraint('idempotency_key'),
    )

    # ── Indexes ─────────────────────────────────────────────────────────

    op.create_index('ix_historial_estado_pedido_pedido_id', 'historial_estado_pedido', ['pedido_id'])
    op.create_index('ix_pago_pedido_id', 'pago', ['pedido_id'])
    op.create_index('ix_pago_external_reference', 'pago', ['external_reference'])
    op.create_index('ix_pago_idempotency_key', 'pago', ['idempotency_key'])
    op.create_index('ix_direccion_entrega_usuario_id', 'direccion_entrega', ['usuario_id'])
    op.create_index('ix_refresh_token_usuario_id', 'refresh_token', ['usuario_id'])
    op.create_index('ix_producto_nombre', 'producto', ['nombre'])
    op.create_index('ix_categoria_nombre', 'categoria', ['nombre'])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index('ix_categoria_nombre')
    op.drop_index('ix_producto_nombre')
    op.drop_index('ix_refresh_token_usuario_id')
    op.drop_index('ix_direccion_entrega_usuario_id')
    op.drop_index('ix_pago_idempotency_key')
    op.drop_index('ix_pago_external_reference')
    op.drop_index('ix_pago_pedido_id')
    op.drop_index('ix_historial_estado_pedido_pedido_id')

    op.drop_table('pago')
    op.drop_table('historial_estado_pedido')
    op.drop_table('detalle_pedido')
    op.drop_table('pedido')
    op.drop_table('producto_ingrediente')
    op.drop_table('producto_categoria')
    op.drop_table('producto')
    op.drop_table('ingrediente')
    op.drop_table('categoria')
    op.drop_table('direccion_entrega')
    op.drop_table('refresh_token')
    op.drop_table('usuario_rol')
    op.drop_table('usuario')
    op.drop_table('unidad_medida')
    op.drop_table('forma_pago')
    op.drop_table('estado_pedido')
    op.drop_table('rol')
