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
| GET | `/tienda` | Abierto/cerrado, horario y zonas de envío activas |
| POST | `/envio/cotizar` | `{ subtotal, ciudad }` → costo envío y mínimo |
| GET | `/catalogo` | Categorías y productos |
| GET | `/formas-pago` | Medios habilitados |
| POST | `/pedidos` | Crear pedido invitado → `tracking_token` |
| GET | `/pedidos/seguimiento/{tracking_token}` | Estado actual |
| GET | `/pedidos/seguimiento/{tracking_token}/historial` | Historial |
| WS | `/ws/seguimiento/{tracking_token}` | Actualizaciones en vivo (`rider_location`, etc.) |
| GET | `/envio/rider/{rider_token}` | Vista repartidor |
| POST | `/envio/rider/{rider_token}/ubicacion` | GPS repartidor → mapa cliente |

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

## Facturación (OWNER)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET/PUT | `/api/v1/facturacion/config` | CUIT, PV, adapter `mock`/`wsfe` |
| GET | `/api/v1/facturacion/pedidos/{id}` | Comprobante del pedido |
| POST | `/api/v1/facturacion/pedidos/{id}/emitir` | Solicitar CAE (mock o WSFE) |

## Caja (OWNER, CASHIER)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/caja/turno/actual` | Turno abierto o null |
| POST | `/api/v1/caja/turno/abrir` | `{ fondo_inicial }` |
| POST | `/api/v1/caja/turno/cerrar` | Arqueo `{ efectivo_contado, notas_cierre? }` |
| POST | `/api/v1/caja/pedidos-mostrador` | Pedido `DINE_IN` ligado al turno |
| POST | `/api/v1/caja/pedidos/{id}/confirmar-cobro` | PENDIENTE → CONFIRMADO en turno abierto |

## Configuración local (OWNER)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/config/horarios` | Horarios semanales + estado actual |
| PUT | `/api/v1/config/horarios` | Guardar 7 días (0=Lunes … 6=Domingo) |
| GET/PUT | `/api/v1/config/delivery-fee` | % comisión apps delivery (KPI ahorro) |
| GET/PUT | `/api/v1/config/zonas-envio` | Zonas por ciudad + default, costo y mínimo |

## Integraciones (OWNER)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/integrations/mp/status` | ¿Conectado? |
| GET | `/api/v1/integrations/mp/authorize-url` | URL OAuth (SPA) |
| GET | `/api/v1/integrations/mp/callback` | Callback MP (público) |

## Catálogo, usuarios, estadísticas

| GET | `/api/v1/estadisticas/ahorro-delivery?desde=&hasta=` | KPI ahorro vs apps delivery (OWNER) |

Ver OpenAPI: `http://localhost:8000/docs` con la API levantada.

Documentación detallada por dominio: `Food-store-admin/BACKEND/README.md`.
