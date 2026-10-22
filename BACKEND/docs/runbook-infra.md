# Runbook infra (borrador M0)

## Repos

| Pieza | Carpeta | Puerto dev (host) |
|-------|---------|-------------------|
| API | `Food-store-admin/BACKEND` | 8000 |
| Admin | `food-store-admin-panel` | **5175** (`npm run dev`) |
| Cliente | `Food-Store-client/store` | 5174 |

Los frontends **no** se construyen desde el `docker-compose.yml` del backend (el viejo `../FRONTEND` ya no existe).

## Docker dev (solo datos)

```powershell
cd Food-store-admin\BACKEND
docker compose up -d db redis
```

- Postgres: `localhost:5555` (user/pass/db según `.env` o defaults del compose).
- Redis: `localhost:6379` → en `.env`: `REDIS_URL=redis://localhost:6379/0`

API en host (recomendado para hot reload):

```powershell
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

API dentro de Docker (perfil `full`):

```powershell
docker compose --profile full up -d
```

## Multi-tenant (opcional)

Por defecto `TENANT_MODE=legacy` (una DB). Para probar multi:

1. `CREATE DATABASE foodstore_control`
2. `alembic -c alembic_control.ini upgrade head`
3. `python -m app.control.seed` (apunta al `POSTGRES_DB` actual)
4. En `.env`: `TENANT_MODE=multi`, `DEFAULT_TENANT_SLUG=demo`
5. Enviar `X-Tenant-Slug: demo` o usar subdominio si configurás `TENANT_BASE_DOMAIN`

Nuevo local: `python scripts/alta_local.py --slug burger --nombre "..." --seed`

## WebSocket y Redis

Sin `REDIS_URL`, los eventos WS solo llegan a clientes conectados al **mismo** proceso Uvicorn.

Con **varios workers** (`--workers 2` o varias réplicas), `REDIS_URL` es obligatorio: pub/sub en canal `foodstore:ws` (configurable con `REDIS_WS_CHANNEL`).

## Producción (esqueleto)

`docker-compose.prod.yml` + `deploy/Caddyfile`. Antes de levantar:

1. Crear `.env.production` (secrets, `CORS_ORIGINS`, MP, Cloudinary).
2. Ajustar dominio en Caddyfile.
3. `docker compose -f docker-compose.prod.yml up -d`

Healthcheck API: `GET /health`.

## Backups

Ver `Food-store-admin/BACKEND/scripts/backup_db.sh` y `restore_db.sh` (contenedor `db` o host con `pg_dump`).

## CI

Workflow `.github/workflows/docker-api.yml`: build de imagen API (sin deploy automático).
