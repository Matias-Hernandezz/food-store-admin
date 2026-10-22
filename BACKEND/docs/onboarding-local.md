# Onboarding de un local nuevo (dev / pre-producción)

Guía para dar de alta un tenant sin Contabo ni credenciales de producción.

## Requisitos

- Docker: Postgres + Redis (`Food-store-admin/BACKEND/docker-compose.yml`)
- Python 3.12, venv en `BACKEND`
- Variables en `.env` (ver `.env.example`): `TENANT_MODE=multi`, DB control, `TOKEN_CIPHER_KEY`, OAuth MP (sandbox)

## 1. Base de control y migraciones

```powershell
cd Food-store-admin\BACKEND
docker compose up -d
alembic -c alembic_control.ini upgrade head
alembic upgrade head
```

## 2. Alta del local

```powershell
python scripts/alta_local.py --slug mi-local --nombre "Mi Local" --db-name foodstore_mi_local
```

Crea la DB del tenant, rol (si aplica), migraciones Alembic en esa DB y usuario OWNER inicial (según flags del script).

## 3. Seed / catálogo demo

```powershell
# Estructural + usuarios demo (modo legacy en una sola DB)
python -m app.db.seed

# Catálogo de prueba (opcional)
python scripts/poblar_catalogo.py
```

En multi-tenant, ejecutá seed/migraciones **en la DB del tenant** (o extendé el script de alta).

## 4. Frontends

**Admin** (`food-store-admin-panel`):

```powershell
copy .env.example .env
# VITE_API_URL=http://localhost:8000
# VITE_TENANT_SLUG=mi-local
npm install
npm run dev
```

**Cliente** (`Food-Store-client/store`):

```powershell
# VITE_USE_PUBLIC_API=true
# VITE_TENANT_SLUG=mi-local
npm run dev
```

## 5. Mercado Pago (sandbox)

1. App en [Mercado Pago Developers](https://www.mercadopago.com.ar/developers) con redirect URI:  
   `http://localhost:8000/api/v1/integrations/mp/callback`
2. En `.env` del backend: `MP_APP_ID`, `MP_CLIENT_SECRET`, `MP_OAUTH_REDIRECT_URI`, `MP_OAUTH_ADMIN_RETURN_URL=http://localhost:5175`
3. En el admin: **Integraciones → Conectar Mercado Pago** (rol OWNER)
4. Webhook de prueba: `POST /webhooks/mp/{slug}` (ver `docs/api.md`)

## 6. Checklist antes del primer cliente real

- [ ] `pytest` en verde (al menos módulos pedidos, pagos, tenant)
- [ ] Pedido guest + seguimiento por token
- [ ] OAuth MP + pago de prueba sandbox
- [ ] Dominio y Contabo (**fuera de alcance** hasta cerrar cliente)
