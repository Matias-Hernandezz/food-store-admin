# API Food Store — resumen

Base URL local: `http://localhost:8000`

En **multi-tenant** (`TENANT_MODE=multi`), enviar header:

```http
X-Tenant-Slug: mi-local
```

## Auth (panel y cliente registrado)

| Método | Ruta | Notas |
|--------|------|--------|
| POST | `/api/v1/auth/register` | Rate limit |
| POST | `/api/v1/auth/login` | Cookie + Bearer |
| POST | `/api/v1/auth/refresh` | |
| GET | `/api/v1/auth/me` | JWT |

Roles staff: `OWNER`, `KITCHEN`, `CASHIER`, `STOCK`. Cliente: `CLIENT`.

## API pública (landings / tienda guest)

Prefijo: `/api/v1/public` — rate limit por IP.

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/tienda` | Estado tienda |
| GET | `/catalogo` | Categorías y productos |
| GET | `/formas-pago` | Medios habilitados |
| POST | `/pedidos` | Crear pedido invitado → `tracking_token` |
| GET | `/pedidos/seguimiento/{tracking_token}` | Estado actual |
| GET | `/pedidos/seguimiento/{tracking_token}/historial` | Historial |
| WS | `/ws/seguimiento/{tracking_token}` | Actualizaciones en vivo |

## Pedidos (autenticado)

| Método | Ruta | Roles |
|--------|------|--------|
| GET/POST | `/api/v1/pedidos/` | CLIENT / staff |
| PATCH | `/api/v1/pedidos/{id}/estado` | FSM por `tipo_pedido` |
| GET | `/api/v1/pedidos/cocina` | KITCHEN, OWNER, … |
| WS | `/api/v1/pedidos/ws/pedidos` | Staff + subscribe por pedido |

## Pagos

| Método | Ruta | Notas |
|--------|------|--------|
| POST | `/api/v1/pagos/crear` | Checkout MP (tenant) |
| GET | `/api/v1/pagos/{pedido_id}` | Estado pago |
| POST | `/webhooks/mp/{slug}` | Webhook MP por local (firma) |

## Integraciones (OWNER)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/integrations/mp/status` | ¿Conectado? |
| GET | `/api/v1/integrations/mp/authorize-url` | URL OAuth (SPA) |
| GET | `/api/v1/integrations/mp/callback` | Callback MP (público) |

## Catálogo, usuarios, estadísticas

Ver OpenAPI: `http://localhost:8000/docs` con la API levantada.

Documentación detallada por dominio: `Food-store-admin/BACKEND/README.md`.
