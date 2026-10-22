"""Verificación de esquema al arranque (sin create_all)."""

import logging

from sqlalchemy import inspect

from app.core.config import settings
from app.core.db import engine

logger = logging.getLogger(__name__)

_SCHEMA_MSG = (
    "Base de datos sin esquema aplicado. Desde la carpeta BACKEND ejecutá:\n"
    "  alembic upgrade head\n"
    "  python -m app.db.seed"
)


def require_schema_ready() -> None:
    """Falla el arranque si faltan tablas (migraciones no aplicadas)."""
    inspector = inspect(engine)
    if not inspector.has_table("rol"):
        logger.error(_SCHEMA_MSG)
        raise RuntimeError("Database schema not initialized. Run alembic upgrade head.")

    if settings.tenant_mode == "multi":
        from app.control.db import get_control_engine

        ctrl = inspect(get_control_engine())
        if not ctrl.has_table("tenants"):
            msg = (
                "DB de control sin esquema. Ejecutá:\n"
                "  alembic -c alembic_control.ini upgrade head"
            )
            logger.error(msg)
            raise RuntimeError("Control database schema not initialized.")
