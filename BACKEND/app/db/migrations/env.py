import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# ── Agregar el proyecto al path ───────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# ── Importar settings para leer DATABASE_URL ──────────────────────────
from app.core.config import settings as app_settings

# ── Importar TODOS los modelos para que SQLModel.metadata los registre ─
import app.modules.dominio_1.Usuarios.models as _u     # noqa: F401
import app.modules.dominio_2.categorias.models as _c     # noqa: F401
import app.modules.dominio_2.ingredientes.models as _i   # noqa: F401
import app.modules.dominio_2.productos.models as _p      # noqa: F401
import app.modules.dominio_2.unidad_medida.models as _m # noqa: F401
import app.modules.dominio_3.pedidos.models as _ped     # noqa: F401
import app.modules.dominio_3.pagos.models as _pag       # noqa: F401

# ── Alembic Config ────────────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Usar la URL de la app en vez de la del .ini
config.set_main_option("sqlalchemy.url", app_settings.DATABASE_URL)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
