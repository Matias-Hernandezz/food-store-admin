# PROMPT MAESTRO: FOOD STORE → PRODUCTO PARA HAMBURGUESERÍAS

Este documento tiene 4 partes. Leelo completo antes de hacer nada.
- Parte 0: cómo trabajar (rol, reglas, decisiones ya tomadas)
- Parte A: infraestructura (VM en Contabo)
- Parte B: aplicación (backend, bases de datos, landings)
- Parte C: cobro local desde el dashboard y facturación electrónica

---

## PARTE 0: CÓMO TRABAJAR

### Rol
Sos un ingeniero senior full-stack (FastAPI/SQLModel/PostgreSQL + React/TypeScript), con experiencia en bases de datos y despliegues en VPS. Trabajás en fases y NO pasás a la siguiente sin mi aprobación explícita.

### Contexto de negocio
Voy a vender a hamburgueserías de Argentina: una landing a medida con el estilo de cada local + sistema de pedidos online propio, SIN comisión por pedido (las apps de delivery cobran entre 25% y 35%). Modelo comercial: un núcleo compartido (pedidos, cocina, pagos, métricas) + una landing personalizada por local, con mensualidad fija. Los primeros 3 a 5 clientes se dan de alta manualmente (no hace falta registro autoservicio ni cobro automático de planes todavía).
Prioridad absoluta: que sea CONFIABLE un viernes a la noche. Un sistema caído o un pedido perdido es un cliente perdido.

### Proyecto actual (verificá todo contra el código real; puede haber cambiado)
- "food_store": proyecto académico ya terminado. Backend FastAPI + SQLModel + PostgreSQL. Frontend en dos repos React + TypeScript (admin y client) con TanStack Query y Zustand (un uiStore por repo).
- Arquitectura backend: dominios (dominio_1 usuarios, dominio_2 catálogo/productos, dominio_3 pedidos) con capas BaseRepository → Unit of Work → Services → Routers.
- Estadísticas: módulo de solo lectura. EstadisticasRepository NO hereda BaseRepository (decisión intencional). Gráficos con Chart.js.
- Imágenes en Cloudinary (transformación c_fill,g_auto). Datos iniciales: seed.py (estructurales) + scripts/poblar_catalogo.py (catálogo demo).
- Repos: [ruta backend], [ruta admin], [ruta client] (en Documents\GitHub).
- Entorno local: Windows + PowerShell + Docker Desktop. Servidor: VM de Contabo (Linux). Dame comandos exactos para cada entorno, indicando cuál es cuál.

### Decisiones ya tomadas (NO las re-evalúes; si ves un problema grave, avisame y esperá)
1. Backend compartido y UNA BASE DE DATOS POR LOCAL. Prohibido compartir DB entre negocios.
2. Una sola VM de Contabo, todo en Docker Compose, con Caddy como reverse proxy.
3. Landings estáticas y separadas del backend (siguen vivas si la API cae, con botón de WhatsApp como plan B).
4. Tiempo real con SSE o WebSocket + Redis pub/sub por local (NO LISTEN/NOTIFY).
5. Cada local cobra en SU PROPIA cuenta de Mercado Pago (OAuth). Yo nunca custodio plata.
6. Cada local es el EMISOR de sus propias facturas (su CUIT, su punto de venta, su certificado).

### Reglas inviolables
1. Respetá la arquitectura existente y las reglas de .cursor/rules (.mdc): controllers finos, prevención de SQL injection, aislamiento contra IDOR, rate limiting. No reescribas lo que funciona; cambios incrementales.
2. No inventes. Si algo no existe en el código, decilo. Citá siempre rutas de archivo como evidencia.
3. Nada destructivo (borrar datos, force push, reset de DB, tocar producción) sin pedírmelo antes.
4. Cambios de esquema SIEMPRE con migraciones (Alembic). Si hoy se usa create_all, proponé la migración a Alembic como tarea separada. Las migraciones deben ser compatibles hacia atrás (agregar antes de usar, no borrar ni renombrar de golpe).
5. Secretos solo por variables de entorno o secretos de Docker. Mantené .env.example actualizado. Nunca commitees credenciales, tokens ni certificados.
6. Dinero: nunca float. Usá Decimal o enteros en centavos, y definí la moneda explícitamente. Fechas en UTC, mostradas en hora de Argentina.
7. Cada tarea: archivos a tocar, criterios de aceptación y tests. Commits chicos con mensajes convencionales.
8. Respondé en español rioplatense, directo, sin relleno, con comandos y código completos y ejecutables.

---

## PARTE A: INFRAESTRUCTURA (VM EN CONTABO)

### A1. Topología
Una VM con Docker Compose. Servicios: `caddy`, `api` (FastAPI con 2 workers y healthcheck), `postgres`, `redis`, `uptime-kuma` y un job de backup. Solo Caddy publica los puertos 80 y 443. Postgres y Redis quedan únicamente en la red interna de Docker. Cloudflare delante (DNS y proxy).

### A2. Sistema base y hardening
- Ubuntu LTS (confirmá la imagen que ofrece Contabo), usuario no-root con sudo, login root deshabilitado.
- SSH solo con llave (sin contraseña), `ufw` abriendo solo 22/80/443, `fail2ban`, `unattended-upgrades`, zona horaria America/Argentina/Buenos_Aires, swap si la RAM es justa.
- Docker: contenedores sin root, imágenes fijadas por versión (no `latest`), límites de CPU/RAM por servicio, rotación de logs.
- Secretos en archivos con permiso 600 o Docker secrets; fuera del repo.

### A3. Proxy y TLS (Caddy)
- HTTPS automático. Subdominios `{slug}.dominio` por local; wildcard por DNS-01 con Cloudflare.
- Dominios propios de cada local con TLS on-demand, con un endpoint `ask` que valide el dominio contra la tabla `tenants` (así nadie puede pedir certificados para dominios ajenos).
- Rate limiting en el proxy, headers de seguridad, restauración de la IP real detrás de Cloudflare.
- Rutas: `/api/*` hacia la API; landings como sitios estáticos (o en Cloudflare Pages).

### A4. PostgreSQL (una instancia)
- Una DB de control (`control`) + una DB por local (`tenant_{slug}`).
- Un rol de Postgres por local con privilegios mínimos sobre su propia DB (segunda barrera si el middleware se equivoca).
- `pg_hba.conf` restrictivo, volumen persistente, parámetros ajustados a la RAM, `max_connections` coherente con los pools.
- Scripts: alta de local (crear DB y rol, migrar, seed, usuario dueño) y baja/archivado de local.

### A5. Redis
Solo red interna, con contraseña. Usos: pub/sub de tiempo real (un canal por local) y rate limiting.

### A6. Backups y recuperación (lo más importante)
- `pg_dump -Fc` de cada DB todas las noches, cifrado y enviado FUERA de la VM (Backblaze B2 o S3, con restic o rclone). Retención sugerida: 7 diarios, 4 semanales, 3 mensuales.
- Test de restauración automático mensual a una DB temporal, con verificación de que los datos existen.
- Alerta si un backup no corrió o falló.
- Snapshot de la VM antes de cambios grandes.
- Runbook `docs/runbook-infra.md` con "cómo levanto todo en otra VM en menos de una hora", probado al menos una vez.

### A7. Deploy sin romper todo
- GitHub Actions: build de la imagen con tag = SHA del commit → push a GHCR → SSH al servidor → `docker compose pull && up -d` esperando el healthcheck.
- Rollback de un solo comando al tag anterior.
- Entorno de staging (un local de prueba) antes de producción. Definí una ventana de deploy fuera del horario de cena y evitá los viernes y sábados a la noche.
- Script `migrar_todos` que recorre todos los locales, aplica Alembic en cada uno y se detiene ante el primer error informando cuáles quedaron actualizados y cuáles no.

### A8. Observabilidad
- Uptime Kuma: checks de la API y de la landing de cada local, con alertas por Telegram o mail.
- Logs en JSON con rotación; request-id y slug del local en cada línea.
- Alertas por disco > 80%, memoria, conexiones de Postgres, backup fallido y vencimiento de certificados (incluidos los certificados de ARCA de cada local, ver Parte C).

### A9. Entregables de infraestructura
`docker-compose.yml` (+ override para desarrollo), `Caddyfile`, `scripts/` (alta_local, baja_local, migrar_todos, backup, restore, rollback), `.github/workflows/`, `docs/runbook-infra.md` y `docs/checklist-hardening.md`.
No prometas ni documentes "100% de disponibilidad": es una sola VM. Documentá qué se puede cumplir (backups diarios, restauración en horas, monitoreo).

---

## PARTE B: APLICACIÓN (BACKEND, BASES DE DATOS Y LANDINGS)

### B1. Backend compartido (FastAPI)
- Mantené las capas BaseRepository → UoW → Services → Routers y los dominios existentes.
- Resolución de local: middleware que obtiene el slug (subdominio, dominio propio o header), lo busca en la DB de control y entrega una sesión de la DB de ese local mediante una dependencia de FastAPI. Cache de engines con tope y pools chicos por local.
- DB de control: `tenants` (slug, estado, datos de conexión cifrados o por convención, configuración), `tenant_domains` y usuarios de plataforma (yo).
- API pública (para las landings): catálogo, horarios, estado abierto/cerrado, zonas de envío, creación de pedido y tracking por token. Con rate limiting, CORS por dominio del local y sin datos sensibles.
- API privada: JWT por local con roles `dueño`, `cocina` y `cajero`. El admin de plataforma es un rol separado, con su propia ruta de acceso.

### B2. Aislamiento
Test obligatorio: pedir datos del local A con el contexto del local B no debe devolver nada. Tests de IDOR por endpoint. Verificá que ninguna consulta pueda salirse de la sesión del local.

### B3. Pedidos y estados (máquina de estados validada en el backend)
- Envío: pendiente → confirmado → en preparación → preparado → enviado → entregado.
- Retiro: pendiente → confirmado → en preparación → preparado → entregado.
- Definí transiciones válidas, cancelación (desde qué estados y con qué motivo) y un historial con fecha, usuario y estado de cada cambio.
- Tipos de pedido: envío, retiro, y presencial/mostrador (ver Parte C).

### B4. Pagos online con Mercado Pago
- Checkout Pro. Cada local conecta su cuenta con OAuth; tokens cifrados en la DB del local.
- Webhook por local `/webhooks/mp/{slug}` con validación de firma e idempotencia. El estado de pago (pendiente, aprobado, rechazado, reembolsado) es independiente del estado del pedido.
- Alternativas: efectivo y transferencia. Documentá cómo probar en sandbox.

### B5. Tiempo real
SSE o WebSocket autenticado, con Redis pub/sub (canal por local) para que funcione con varios workers. Reconexión automática y polling como respaldo. Aviso sonoro en el panel cuando entra un pedido.

### B6. Cocina (KDS) y seguimiento del cliente
- KDS: columnas por estado, tarjetas grandes, tiempo transcurrido; el rol `cocina` solo ve y avanza pedidos.
- Seguimiento: página pública con token (sin login) que muestra el estado según sea envío o retiro y se actualiza en vivo. Dejá preparado el gancho para avisos por WhatsApp.

### B7. Métricas y catálogo
- Métricas: ventas por período, ticket promedio, pedidos por estado, productos top, horarios pico, ingresos por forma de pago, comparación con el período anterior y "ahorro estimado vs. apps de delivery" (con % de comisión configurable por local).
- Catálogo (CRUD): categorías, productos, variantes y extras (doble carne, sin cebolla), combos, disponibilidad ("agotado" en un clic), imágenes en Cloudinary y precios.
- Extras (marcá prioridad P1/P2 y justificá): horarios con apertura y cierre automático, zonas de envío con costo y pedido mínimo, cupones, pedidos programados, historial y recompra de clientes, QR, exportación de reportes.

### B8. Bases de datos
- Una DB por local con el esquema completo del producto; Alembic para la DB de control y para las de los locales.
- Convenciones: dinero en Decimal o centavos, fechas en UTC, borrado lógico en pedidos y pagos, tabla de auditoría para acciones sensibles (anulaciones, cambios de precio, cambios de estado).
- Índices para listados frecuentes, paginación obligatoria, y seed estructural separado del catálogo demo.
- Plan de migración del esquema actual a este modelo, con sus riesgos.

### B9. Landings por local
- Plantilla base separada del backend (React + Vite, build estático) con un archivo de tema por local (colores, tipografía, logo, hero, textos, redes). Dar de alta un local = copiar plantilla + tema + correr el script de alta.
- Consume la API pública del local. Si la API no responde, muestra el menú en modo lectura y un botón "Pedí por WhatsApp".
- SEO (meta, Open Graph, schema.org Restaurant), performance y accesibilidad. Despliegue independiente del backend.
- Recomendá qué hacer con los dos repos React actuales (por ejemplo, convertir `client` en la plantilla con tema y dejar `admin` como panel del dueño, cocina y caja).
- Checklist de onboarding de un local nuevo (datos, menú, fotos, Mercado Pago, horarios, zonas, dominio).

### B10. Entregables de aplicación
Auditoría, specs por feature, tests (pytest para estados, webhooks idempotentes y aislamiento entre locales; smoke tests del frontend), `README` actualizado, `docs/onboarding-local.md` y `docs/api.md`.

---

## PARTE C: COBRO LOCAL Y FACTURACIÓN (desde el dashboard)

Prioridad P2: se implementa DESPUÉS de que el núcleo (Partes A y B) esté estable. Diseñalo ahora para que no haya que rehacer nada, pero no lo construyas antes.

### C1. Cobro presencial en el local
- Crear un pedido presencial (mostrador o salón) desde el panel, o cobrar un pedido existente (por ejemplo, retiro que paga en el local).
- Medios de pago: efectivo (con cálculo de vuelto), tarjeta de débito/crédito (terminal externa, registrada manualmente), transferencia y Mercado Pago QR. Pagos divididos o parciales, descuentos y propina.
- Caja: apertura y cierre de turno, arqueo, movimientos de caja (ingresos y egresos), reporte por turno y por medio de pago.
- Rol `cajero` con permisos limitados. Anulaciones y devoluciones con motivo y auditoría. Ticket imprimible.
- P3 (evaluar): integración con terminal Mercado Pago Point, solo si la API vigente lo permite.

### C2. Facturación electrónica (ARCA, ex AFIP)
- Cada local es el EMISOR: su CUIT, su punto de venta de tipo "Web Services" y su certificado digital. Yo no facturo a nombre propio.
- Comprobantes: Factura C si el local es monotributista; A/B si es responsable inscripto; consumidor final según corresponda. Notas de crédito para anulaciones. Cada punto de venta y tipo de comprobante tiene su numeración correlativa.
- Web services: investigá y decidí entre `wsfev1` (A/B/C sin detalle de ítems) y `wsmtxca` (con ítems), según lo que realmente necesitemos. Autenticación por WSAA con certificado X.509 (cachear tokens), con entornos de homologación y producción bien separados.
- Flujo: cobro → (opcional o automático según config del local) emisión → CAE → PDF con QR → envío al cliente. Manejo de timeouts y errores con reintentos idempotentes, un estado "pendiente de CAE" y la garantía de no duplicar comprobantes.
- Certificados y claves por local, cifrados con una clave maestra guardada fuera de la DB. Alerta de vencimiento.
- Arquitectura: definí un puerto `Facturador` con dos posibles adaptadores: (1) integración directa con WSFE con una librería, o (2) un proveedor externo con API/SDK. Compará costo, riesgo y mantenimiento, recomendá uno y justificá. Empezá siempre en homologación.
- Checklist de onboarding de facturación por local (clave fiscal, alta del punto de venta Web Services, relación con el servicio de facturación electrónica, certificado, pruebas).
- Aviso: esto no es asesoramiento contable ni fiscal. Cada local debe validar su condición y sus alícuotas con su contador. No emitas nada en producción sin pruebas completas en homologación.

---

## FASES Y ENTREGAS

### FASE 0: AUDITORÍA (solo lectura, NO modifiques código)
Entregable: `docs/auditoria.md` con:
1. Mapa de arquitectura actual y flujo de un pedido de punta a punta.
2. Tabla de requerimientos de las Partes A, B y C con estado ✅ completo / ⚠️ parcial / ❌ falta, con evidencia (archivos).
3. Bugs, código muerto, inconsistencias entre backend y los dos frontends, y deuda técnica.
4. Riesgos de seguridad (auth, roles, IDOR, validaciones, CORS, rate limiting, secretos).
5. Tests existentes y qué es imprescindible testear.
6. Qué bloquea producción hoy.
7. Qué hay que cambiar para soportar una DB por local con backend compartido.
Al terminar, frená y esperá mi aprobación.

### FASE 1: PLAN (SDD), después de aprobar la auditoría
Por milestone: propuesta → spec → diseño → tareas ordenadas, con estimación relativa (S/M/L) y dependencias.
- M0: infraestructura base (VM, compose, Caddy, backups, monitoreo, CI/CD). Puede avanzar en paralelo.
- M1: núcleo confiable (pedidos + máquina de estados + Mercado Pago + migraciones + tests).
- M2: tiempo real, cocina y seguimiento del cliente.
- M3: una DB por local, roles, resolución de local y landings con tema.
- M4: métricas (incluido el ahorro vs. apps) y extras P1.
- M5: cobro local y caja (Parte C1).
- M6: facturación electrónica (Parte C2).
- M7: hardening, runbooks y documentación final.
Esperá mi aprobación antes de implementar.

### FASE 2: IMPLEMENTACIÓN
De a una tarea por vez, en el orden del plan. Por cada tarea: qué cambia, archivos, comandos exactos para correr y probar (aclarando PowerShell local o bash en la VM), tests y criterio de aceptación cumplido. No toques nada fuera del alcance de la tarea.

### FORMATO DE ENTREGA DE CADA FASE
Resumen de 5 líneas máximo + el documento correspondiente en `docs/` + lista de decisiones que necesitás que yo tome (con tu recomendación para cada una).

### IGNORE
Ignora los otros archivos que estan en /docs, ya no los necesitamos. No los borres ni modifiques.