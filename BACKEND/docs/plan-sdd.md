# Fase 1 — Plan SDD (Software Design & Delivery)

**Aprobado:** auditoría Fase 0 + directivas del productor (2026-10-21)  
**Ramas de trabajo:** `feat/nuevas-mejoras` en los tres repos  
**Fuera de alcance explícito:** diseño visual / tema de landings por hamburguesería (se hace al cerrar el primer cliente).

---

## Decisiones de diseño (cerradas)

### Roles (códigos en DB y JWT)

| Código | Etiqueta UI (es-AR) | Reemplaza | Alcance |
|--------|---------------------|-----------|---------|
| `OWNER` | Dueño | `ADMIN` | Todo el local: usuarios, catálogo, pedidos, estadísticas, configuración futura |
| `KITCHEN` | Cocina | parte de `PEDIDOS` | KDS, avanzar estados de preparación |
| `CASHIER` | Cajero | parte de `PEDIDOS` | Kanban, cajero, confirmar pagos en mostrador |
| `STOCK` | Stock | — | Catálogo, disponibilidad, ingredientes |
| `CLIENT` | Cliente | — | Tienda online, pedidos propios |

**Futuro M3:** rol `PLATFORM` (vos) en DB `control`, separado de roles de tenant.

Migración: usuarios con `PEDIDOS` reciben **KITCHEN + CASHIER**. Sin rol `ADMIN` / `PEDIDOS` en código nuevo.

### Estados de pedido (códigos)

| Código | Descripción | Notas |
|--------|-------------|--------|
| `PENDIENTE` | Creado, pago pendiente | — |
| `CONFIRMADO` | Pagado / aceptado | — |
| `EN_PREPARACION` | En cocina | Renombre de `EN_PREP` (migración datos) |
| `PREPARADO` | Listo para retiro/envío | **Nuevo** |
| `EN_CAMINO` | En camino (solo envío) | **Nuevo** |
| `ENTREGADO` | Cerrado | Terminal |
| `CANCELADO` | Cancelado | Terminal |

**Tipo de pedido** (`tipo_pedido` en `pedido`): `DELIVERY` | `PICKUP` | `DINE_IN` (mostrador — usado fuerte en M5).

FSM por tipo (validación en `PedidoService`):

- **DELIVERY:** PENDIENTE → CONFIRMADO → EN_PREPARACION → PREPARADO → EN_CAMINO → ENTREGADO (+ CANCELADO donde aplique).
- **PICKUP:** igual sin `EN_CAMINO`.
- **DINE_IN:** PENDIENTE → CONFIRMADO → EN_PREPARACION → PREPARADO → ENTREGADO (M5 refina caja).

---

## Milestones

### M0 — Infra base (paralelo, sin bloquear M1)

| ID | Tarea | Tamaño | Depende |
|----|-------|--------|---------|
| M0.1 | `docker-compose.prod.yml` esqueleto: caddy, api, postgres, redis (sin landings) | M | — |
| M0.2 | Corregir compose dev: quitar build `FRONTEND`, documentar 3 repos | S | — |
| M0.3 | `docs/runbook-infra.md` borrador + `docs/checklist-hardening.md` | M | M0.1 |
| M0.4 | Workflow GH Actions build/push imagen API (sin deploy automático aún) | M | M0.1 |
| M0.5 | Scripts `scripts/backup_db.sh`, `restore_db.sh` (una DB por ahora) | S | — |

### M1 — Núcleo confiable (prioridad actual)

| ID | Tarea | Tamaño | Depende |
|----|-------|--------|---------|
| M1.1 | Deps backend (`psycopg[binary]`, `python-multipart`) + README setup | S | — |
| M1.2 | Fix IDOR `GET /pedidos/{id}/historial` + tests | S | — |
| M1.3 | WS: broadcast staff-only (`OWNER`,`KITCHEN`,`CASHIER`); clientes solo `order:{id}` | S | — |
| M1.4 | Renombre roles + migración Alembic + seed + tests + admin/client | M | M1.1 |
| M1.5 | `tipo_pedido` + estados nuevos + FSM por tipo + migración `EN_PREP`→`EN_PREPARACION` | L | M1.4 |
| M1.6 | Webhook MP: firma obligatoria cuando hay body; tests rechazo | S | M1.1 |
| M1.7 | Quitar `create_all` del lifespan; arranque con Alembic documentado | M | M1.5 | ✅ |
| M1.8 | Seguimiento cliente: `useOrderStatusWS` suscribe pedidos activos del usuario | S | M1.3 |

**Criterio M1 listo:** pytest verde; FSM y roles alineados en back + admin; sin IDOR historial; venv fresco levanta API.

### M2 — Tiempo real productivo

| ID | Tarea | Tamaño | Depende |
|----|-------|--------|---------|
| M2.1 | Redis pub/sub + adaptador WS | L | M0.1, M1 |
| M2.2 | Sonido nuevo pedido en admin (ya hay gancho UI) | S | M2.1 |
| M2.3 | Polling fallback si WS cae | S | M2.1 |

### M3 — Multi-tenant (sin diseño landing)

| ID | Tarea | Tamaño | Depende |
|----|-------|--------|---------|
| M3.1 | DB `control` + modelos `tenants`, `tenant_domains` | L | M1.7 |
| M3.2 | Middleware slug + `get_tenant_session` + cache engines | L | M3.1 |
| M3.3 | Scripts `alta_local`, `baja_local`, `migrar_todos` | M | M3.2 |
| M3.4 | MP OAuth por tenant + webhook `/webhooks/mp/{slug}` | L | M3.2 | ✅ |
| M3.5 | API pública (catálogo, crear pedido, tracking por token) | M | M3.2 |
| M3.6 | Tests aislamiento A≠B | M | M3.2 | ✅ |
| M3.7 | Cliente actual como **shell** tienda (sin tema visual nuevo) | M | M3.5 | ⚠️ API pública + guest checkout + `/seguimiento/:token` |

### M4 — Métricas y extras P1

| ID | Tarea | Tamaño | Depende |
|----|-------|--------|---------|
| M4.1 | KPI “ahorro vs delivery” (% configurable por tenant) | M | M3 |
| M4.2 | Horarios apertura/cierre + “cerrado” automático | M | M3 |
| M4.3 | Zonas de envío + mínimo de pedido | L | M3 |

### M5 — Caja local (Parte C1)

Pedido mostrador, turnos, arqueo, rol `CASHIER` acotado.

### M6 — Facturación ARCA (Parte C2)

Puerto `Facturador` + homologación; sin producción sin pruebas.

### M7 — Hardening y docs finales

`onboarding-local.md`, `api.md`, runbook probado.

---

## Orden de implementación inmediato (Fase 2)

1. **M1.1** — requirements  
2. **M1.2** — historial IDOR  
3. **M1.3** — WS staff  
4. **M1.4** — roles OWNER/KITCHEN/CASHIER (en curso)  
5. **M1.5** — FSM extendida  
6. **M1.6** — webhook  
7. Paralelo liviano: **M0.2** compose dev  

Cada tarea: PR/commit chico en `feat/nuevas-mejoras`, mensaje convencional.

---

## Riesgos y mitigación

| Riesgo | Mitigación |
|--------|------------|
| Renombre roles rompe sesiones JWT viejas | Re-login; deploy en ventana baja |
| Migración estados con pedidos `EN_PREP` en vuelo | Migración SQL UPDATE + compat en lectura 1 release |
| Multi-DB sin Redis | M2 antes de escalar workers en prod |
| Landings diferidas | API pública M3.5 + cliente actual hasta diseño por cliente |

---

## Formato de cierre Fase 1

- Este documento = propuesta + spec + tareas ordenadas.  
- **Implementación** arranca en M1.1 sin esperar otro OK (aprobación implícita: “mandale mecha”).  
- Próximo checkpoint: M1 completo → demo local viernes simulado (pedido MP + cocina + estados).
