"""roles_owner_kitchen_cashier

Revision ID: d4e8f1a2b3c4
Revises: c3308d83eb84
Create Date: 2026-10-21 19:55:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "d4e8f1a2b3c4"
down_revision: Union[str, None] = "c3308d83eb84"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO rol (codigo, nombre, descripcion) VALUES
            ('OWNER', 'Dueño', 'Administración del local'),
            ('KITCHEN', 'Cocina', 'Preparación de pedidos'),
            ('CASHIER', 'Cajero', 'Caja y gestión de pedidos')
        ON CONFLICT (codigo) DO NOTHING
        """
    )
    op.execute("UPDATE usuario_rol SET rol_codigo = 'OWNER' WHERE rol_codigo = 'ADMIN'")
    op.execute(
        """
        INSERT INTO usuario_rol (usuario_id, rol_codigo, asignado_por_id, expires_at, created_at)
        SELECT usuario_id, 'KITCHEN', asignado_por_id, expires_at, COALESCE(created_at, NOW())
        FROM usuario_rol WHERE rol_codigo = 'PEDIDOS'
        ON CONFLICT DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO usuario_rol (usuario_id, rol_codigo, asignado_por_id, expires_at, created_at)
        SELECT usuario_id, 'CASHIER', asignado_por_id, expires_at, COALESCE(created_at, NOW())
        FROM usuario_rol WHERE rol_codigo = 'PEDIDOS'
        ON CONFLICT DO NOTHING
        """
    )
    op.execute("DELETE FROM usuario_rol WHERE rol_codigo = 'PEDIDOS'")
    op.execute("DELETE FROM rol WHERE codigo IN ('ADMIN', 'PEDIDOS')")


def downgrade() -> None:
    op.execute(
        """
        INSERT INTO rol (codigo, nombre, descripcion) VALUES
            ('ADMIN', 'Administrador', 'CRUD completo del sistema'),
            ('PEDIDOS', 'Gestor de Pedidos', 'Ver y avanzar estados de pedidos')
        ON CONFLICT (codigo) DO NOTHING
        """
    )
    op.execute("UPDATE usuario_rol SET rol_codigo = 'ADMIN' WHERE rol_codigo = 'OWNER'")
    op.execute(
        """
        INSERT INTO usuario_rol (usuario_id, rol_codigo, asignado_por_id, expires_at, created_at)
        SELECT DISTINCT ON (usuario_id) usuario_id, 'PEDIDOS', asignado_por_id, expires_at,
            COALESCE(created_at, NOW())
        FROM usuario_rol
        WHERE rol_codigo IN ('KITCHEN', 'CASHIER')
        ORDER BY usuario_id, rol_codigo
        ON CONFLICT DO NOTHING
        """
    )
    op.execute("DELETE FROM usuario_rol WHERE rol_codigo IN ('OWNER', 'KITCHEN', 'CASHIER')")
    op.execute("DELETE FROM rol WHERE codigo IN ('OWNER', 'KITCHEN', 'CASHIER')")
