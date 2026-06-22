# 🍔 Food Store — Admin + Backend
PRESENTACION: https://drive.google.com/drive/folders/143_vULtd3kLN0iALQ0OFWoC-zm7B3HEr?usp=sharing
Aplicacion full-stack para la gestion integral de un negocio de comidas. Backend FastAPI + PostgreSQL + MercadoPago + Cloudinary + WebSocket. Panel de administracion React con dashboard, CRUD de entidades y gestion de pedidos en tiempo real.

## Stack Tecnologico

| Capa | Tecnologia |
|------|-----------|
| Backend | FastAPI 0.111+ · SQLModel 0.0.19+ · PostgreSQL 15+ |
| Auth | JWT (python-jose) · bcrypt (passlib, cost≥12) |
| Pagos | MercadoPago SDK Python 2.3+ (Checkout PRO, PCI SAQ-A) |
| Imagenes | Cloudinary SDK Python 1.x+ |
| WebSocket | FastAPI WebSocket nativo |
| Rate Limiting | SlowAPI (5 intentos / 15 min en login) |
| Frontend Admin | React 19 · TypeScript 5.x · Vite 5.x · Tailwind CSS 3.x |
| Estado | Zustand 4.x · TanStack Query 5.x |
| Graficos | Recharts 2.x |
| Testing | Pytest · TestClient (httpx) · PostgreSQL |

## Prerequisitos

- **Python** 3.11+
- **Node.js** 20+ + **pnpm** 9+
- **PostgreSQL** 15+ corriendo en `localhost:5432`

---

## Setup — Paso a Paso

### 1. Crear la base de datos

```powershell
# Reemplaza "postgres" por tu usuario de PostgreSQL si es distinto
createdb -U postgres foodstore_db
```

### 2. Configurar variables de entorno

```powershell
cd BACKEND
copy .env.example .env
```

Editar `BACKEND/.env` y completar estas variables:

| Variable | Valor de ejemplo |
|----------|-----------------|
| `SECRET_KEY` | `clave-secreta-de-al-menos-32-caracteres` |
| `MP_ACCESS_TOKEN` | `TEST-1234567890123456-123456` (MercadoPago) |
| `CLOUDINARY_CLOUD_NAME` | Tu cloud name de Cloudinary |
| `CLOUDINARY_API_KEY` | Tu API Key de Cloudinary |
| `CLOUDINARY_API_SECRET` | Tu API Secret de Cloudinary |

> 💡 Credenciales MP: https://www.mercadopago.com.ar/developers/panel  
> 💡 Credenciales Cloudinary: https://console.cloudinary.com

### 3. Instalar dependencias del backend

```powershell
cd BACKEND
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Poblar la base de datos

```powershell
python -m app.db.seed
```

**Esto crea todas las tablas y carga los datos iniciales:**
- 4 roles (ADMIN, STOCK, PEDIDOS, CLIENT)
- 5 estados de pedido (PENDIENTE → CONFIRMADO → EN_PREP → ENTREGADO / CANCELADO)
- 3 formas de pago (MERCADOPAGO, EFECTIVO, TRANSFERENCIA)
- 6 unidades de medida (kg, g, L, ml, ud, porciones)
- 12 categorias jerarquicas + 87 ingredientes + 45 productos
- Usuario admin + 3 usuarios de prueba
- 20 pedidos de prueba

```powershell
# Verifica que termine con:
#   Seed completado
#   Email    : admin@foodstore.com
#   Password : Admin1234!
```

### 5. Levantar el backend

```powershell
uvicorn app.main:app --reload
```

Backend disponible en **http://localhost:8000**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 6. Levantar el panel de administracion

En otra terminal:

```powershell
cd FRONTEND
copy .env.example .env
pnpm install
pnpm dev
```

Admin disponible en **http://localhost:5174**

---

## Credenciales de Acceso

| Rol | Email | Password |
|-----|-------|----------|
| Admin | admin@foodstore.com | Admin1234! |
| Stock | stock@ejemplo.com | 123456 |
| Pedidos | pedidos@ejemplo.com | 123456 |
| Cliente | user@ejemplo.com | 123456 |

---

## API Endpoints

Todos los endpoints usan el prefijo `/api/v1`. Documentacion completa en `/docs`.

### Auth
| Metodo | Endpoint | Auth |
|--------|----------|------|
| POST | `/auth/register` | Publico |
| POST | `/auth/login` | Publico (rate limited: 5/15min) |
| POST | `/auth/refresh` | Cookie |
| POST | `/auth/logout` | Bearer |
| GET | `/auth/me` | Bearer |
| GET | `/auth/usuarios` | ADMIN |
| PATCH | `/auth/usuarios/{id}` | ADMIN |
| DELETE | `/auth/usuarios/{id}` | ADMIN |

### Productos
| Metodo | Endpoint | Auth |
|--------|----------|------|
| GET | `/productos` | Publico |
| GET | `/productos/{id}` | Publico |
| POST | `/productos` | ADMIN |
| PATCH | `/productos/{id}` | ADMIN, STOCK |
| PATCH | `/productos/{id}/disponibilidad` | ADMIN, STOCK |
| PATCH | `/productos/{id}/imagenes` | ADMIN |
| DELETE | `/productos/{id}` | ADMIN |
| GET | `/productos/{id}/ingredientes` | Publico |
| POST | `/productos/{id}/ingredientes` | ADMIN |

### Pedidos
| Metodo | Endpoint | Auth |
|--------|----------|------|
| GET | `/pedidos` | CLIENT/ADMIN/PEDIDOS |
| POST | `/pedidos` | CLIENT |
| GET | `/pedidos/{id}` | Propietario/ADMIN |
| PATCH | `/pedidos/{id}/estado` | ADMIN/PEDIDOS |
| DELETE | `/pedidos/{id}` | CLIENT propietario |
| GET | `/pedidos/{id}/historial` | Propietario/ADMIN |
| GET | `/pedidos/cocina` | ADMIN/PEDIDOS |

### Pagos (MercadoPago)
| Metodo | Endpoint | Auth |
|--------|----------|------|
| POST | `/pagos/crear` | CLIENT |
| POST | `/pagos/webhook` | Publico (HMAC) |
| GET | `/pagos/{pedido_id}` | Propietario/ADMIN |

### Uploads (Cloudinary)
| Metodo | Endpoint | Auth |
|--------|----------|------|
| POST | `/uploads/imagen` | ADMIN |
| DELETE | `/uploads/imagen/{public_id}` | ADMIN |

### Estadisticas
| Metodo | Endpoint | Auth |
|--------|----------|------|
| GET | `/estadisticas/resumen` | ADMIN |
| GET | `/estadisticas/ventas` | ADMIN |
| GET | `/estadisticas/productos-top` | ADMIN |
| GET | `/estadisticas/pedidos-por-estado` | ADMIN |
| GET | `/estadisticas/ingresos` | ADMIN |

### WebSocket
| Endpoint | Auth |
|----------|------|
| `ws://localhost:8000/api/v1/pedidos/ws/pedidos?token=JWT` | JWT en query param |

---

## Estructura del Proyecto

```
Food-store-admin/
├── BACKEND/
│   ├── app/
│   │   ├── main.py                    # FastAPI entry point
│   │   ├── core/                      # config, db, security, UoW, WS, rate limit
│   │   ├── db/                        # seed.py + migraciones Alembic
│   │   └── modules/
│   │       ├── dominio_1/Usuarios/    # Auth, RBAC, direcciones
│   │       ├── dominio_2/             # Catalogo: Categoria, Producto, Ingrediente, UnidadMedida
│   │       ├── dominio_3/             # Ventas: Pedidos (FSM), Pagos (MercadoPago)
│   │       ├── estadisticas/          # Dashboard KPIs
│   │       └── uploads/              # Cloudinary
│   ├── tests/                         # pytest (auth, pedidos, pagos, estadisticas, uploads, websocket)
│   ├── requirements.txt
│   ├── alembic.ini
│   └── .env.example
└── FRONTEND/                          # Panel de administracion (React + Vite)
    └── src/
        ├── features/
        │   ├── auth/                  # Login, registro
        │   ├── panel/                 # Dashboard + graficos Recharts
        │   ├── pedidos/               # Kanban, cocina, cajero, estadisticas
        │   ├── producto/              # CRUD + Cloudinary upload
        │   ├── categoria/             # CRUD
        │   ├── ingrediente/           # CRUD
        │   └── usuarios/              # CRUD + roles
        └── shared/                    # API client, hooks, components
```

## Arquitectura

### Backend — Capas (flujo unidireccional)

```
Router → Service → UnitOfWork → Repository → Model
                          ↑
                    WSManager (post-commit)
```

- **Router**: HTTP puro, parsea request, valida schemas, delega al Service
- **Service**: Logica de negocio stateless, opera dentro del UoW
- **Unit of Work**: Transaccion atomica, commit/rollback automatico
- **Repository**: Acceso a BD, consultas sin logica de negocio. `BaseRepository[T]` generico
- **Model**: SQLModel tables + relaciones
- **WSManager**: Broadcast de eventos post-commit, FUERA del bloque UoW

### Patrones aplicados

| Patron | Descripcion |
|--------|-------------|
| Repository | `BaseRepository[T]` generico, abstrae acceso a BD |
| Unit of Work | Transacciones atomicas con context manager |
| Service Layer | Logica stateless, independiente del framework |
| Snapshot | Precios/nombres inmutables al crear pedido |
| Soft Delete | `deleted_at TIMESTAMPTZ`, nunca DELETE fisico |
| Audit Trail | `HistorialEstadoPedido` append-only (solo INSERT) |
| State Machine | FSM 5 estados con transiciones validadas |
| Idempotent Payments | UUID `idempotency_key` evita cobros duplicados |

---

## Tests

```powershell
cd BACKEND

# Crear BD de test
createdb -U postgres foodstore_test

# Ejecutar tests
pytest tests/ -v

# Con cobertura
pip install pytest-cov
pytest tests/ --cov=app --cov-report=term-missing
```

| Archivo | Modulo |
|---------|--------|
| `test_auth.py` | Registro, login, logout, refresh, rate limit |
| `test_pedidos.py` | Crear pedido, FSM, cancelar, historial append-only |
| `test_pagos.py` | Crear pago, webhook, idempotencia (mocks MP) |
| `test_estadisticas.py` | KPIs, EST-01/02/03, productos top |
| `test_uploads.py` | Upload, delete, validacion (mocks Cloudinary) |
| `test_websocket.py` | Conexion, autenticacion, suscripcion |

---

## Checklist de Rubrica

| Codigo | Item |
|--------|------|
| CE-01 | Repositorio GitHub publico |
| CE-02 | README con instrucciones de setup |
| CE-03 | `.env.example` completo (MP, Cloudinary, WS) |
| CE-05 | `python -m app.db.seed` ejecuta correctamente |
| CE-07 | `pip install -r requirements.txt + uvicorn` sin errores |
| CE-08 | Swagger UI (`/docs`) accesible |
| CE-09 | Pago de prueba MP end-to-end + notificacion WS |
| CE-10 | Unit of Work sin `session.commit()` directo |
| CE-11 | 5 Zustand stores tipados con persist |
| CE-12 | WebSocket: cambio de estado actualiza UI sin recargar |
| CE-13 | Cloudinary: subir imagen desde admin y verla en catalogo |
| CE-15 | Video demostracion (10-15 min) |
| CE-16 | Repositorio publico verificado |

## Tarjetas de Prueba — MercadoPago

| Importe | Resultado |
|---------|-----------|
| < $200 | Aprobado |
| $200 – $600 | Pendiente |
| > $600 | Rechazado |

**Numero:** `5031 7557 3453 0604` | **Vencimiento:** cualquiera | **CVV:** `123` | **Titular:** `APRO`

---

Proyecto academico — Food Store v6.0
