# Migraciones de base de datos (Alembic)

El backend **no** crea tablas al arrancar (`create_all` fue removido del lifespan). El esquema se aplica solo con Alembic.

## Setup local (PowerShell)

```powershell
cd Food-store-admin\BACKEND
.\venv\Scripts\activate

# Crear DB si no existe (ejemplo)
# createdb -U postgres db-parcial-1

alembic upgrade head
python -m app.db.seed
```

## Comandos útiles

| Comando | Uso |
|---------|-----|
| `alembic current` | Revisión aplicada |
| `alembic history` | Historial de revisiones |
| `alembic upgrade head` | Aplicar todas las migraciones pendientes |
| `alembic downgrade -1` | Revertir una revisión (solo dev) |

## Base vieja sin `alembic_version`

Si tenías tablas creadas con `create_all` y el esquema ya coincide con `head`:

```powershell
alembic stamp head
alembic upgrade head
```

Si el esquema está desfasado, respaldá la DB y aplicá `upgrade head` (puede requerir migración manual de datos).

## Tests

Pytest usa `SKIP_DB_SCHEMA_CHECK=1` y crea el esquema con `SQLModel.metadata.create_all` en la DB `foodstore_test` (ver `tests/conftest.py`).

## Producción

1. Imagen Docker / deploy ejecuta `alembic upgrade head` **antes** de levantar uvicorn.
2. El API falla al iniciar si no existe la tabla `rol` (esquema no aplicado).

## DB de control (multi-tenant)

Cuando `TENANT_MODE=multi`, además de cada DB `tenant_{slug}`:

```powershell
# Crear DB de control (una vez)
psql -U postgres -c "CREATE DATABASE foodstore_control"

alembic -c alembic_control.ini upgrade head
python -m app.control.seed --slug demo --db-name db-parcial-1
```

| Comando | Uso |
|---------|-----|
| `alembic -c alembic_control.ini upgrade head` | Esquema control |
| `python scripts/alta_local.py --slug X --nombre "..."` | Nueva DB + migración + registro |
| `python scripts/migrar_todos.py` | Alembic en todos los tenants activos |
| `python scripts/set_mp_tokens.py --slug X --access-token ...` | Token MP del local en control |

En dev podés seguir con `TENANT_MODE=legacy` (default) y una sola `POSTGRES_DB`.
