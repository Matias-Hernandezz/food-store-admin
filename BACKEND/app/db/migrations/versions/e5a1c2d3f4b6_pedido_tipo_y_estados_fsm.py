"""pedido_tipo_y_estados_fsm

Revision ID: e5a1c2d3f4b6
Revises: d4e8f1a2b3c4
Create Date: 2026-10-21 20:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "e5a1c2d3f4b6"
down_revision: Union[str, None] = "d4e8f1a2b3c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO estado_pedido (codigo, descripcion, orden, es_terminal) VALUES
            ('EN_PREPARACION', 'En preparación en cocina', 3, false),
            ('PREPARADO', 'Listo para retiro o envío', 4, false),
            ('EN_CAMINO', 'En camino al cliente', 5, false)
        ON CONFLICT (codigo) DO NOTHING
        """
    )
    op.execute(
        """
        UPDATE pedido SET estado_codigo = 'EN_PREPARACION' WHERE estado_codigo = 'EN_PREP'
        """
    )
    op.execute(
        """
        UPDATE historial_estado_pedido SET estado_desde = 'EN_PREPARACION'
        WHERE estado_desde = 'EN_PREP'
        """
    )
    op.execute(
        """
        UPDATE historial_estado_pedido SET estado_hacia = 'EN_PREPARACION'
        WHERE estado_hacia = 'EN_PREP'
        """
    )
    op.execute("DELETE FROM estado_pedido WHERE codigo = 'EN_PREP'")
    op.execute("UPDATE estado_pedido SET orden = 6, es_terminal = true WHERE codigo = 'ENTREGADO'")
    op.execute("UPDATE estado_pedido SET orden = 7, es_terminal = true WHERE codigo = 'CANCELADO'")

    op.add_column(
        "pedido",
        sa.Column("tipo_pedido", sa.String(length=20), nullable=False, server_default="DELIVERY"),
    )
    op.execute(
        """
        UPDATE pedido SET tipo_pedido = CASE
            WHEN direccion_id IS NULL THEN 'PICKUP'
            ELSE 'DELIVERY'
        END
        """
    )


def downgrade() -> None:
    op.drop_column("pedido", "tipo_pedido")

    op.execute(
        """
        INSERT INTO estado_pedido (codigo, descripcion, orden, es_terminal) VALUES
            ('EN_PREP', 'En preparación en cocina', 3, false)
        ON CONFLICT (codigo) DO NOTHING
        """
    )
    op.execute(
        """
        UPDATE pedido SET estado_codigo = 'EN_PREP' WHERE estado_codigo = 'EN_PREPARACION'
        """
    )
    op.execute(
        """
        UPDATE historial_estado_pedido SET estado_desde = 'EN_PREP'
        WHERE estado_desde = 'EN_PREPARACION'
        """
    )
    op.execute(
        """
        UPDATE historial_estado_pedido SET estado_hacia = 'EN_PREP'
        WHERE estado_hacia = 'EN_PREPARACION'
        """
    )
    op.execute("DELETE FROM estado_pedido WHERE codigo IN ('EN_PREPARACION', 'PREPARADO', 'EN_CAMINO')")
    op.execute("UPDATE estado_pedido SET orden = 4 WHERE codigo = 'ENTREGADO'")
    op.execute("UPDATE estado_pedido SET orden = 5 WHERE codigo = 'CANCELADO'")
