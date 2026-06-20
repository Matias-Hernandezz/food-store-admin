import logging
import os
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded

from app.core.db import create_all_tables
from app.core.rate_limit import limiter
from app.modules.dominio_1.Usuarios.routers import router as router_auth
from app.modules.dominio_2.Categoria.routers import router as router_categoria
from app.modules.dominio_2.Ingrediente.routers import router as router_ingrediente
from app.modules.dominio_2.Producto.routers import router as router_producto
from app.modules.dominio_2.unidad_medida.router import router as router_unidad_medida
from app.modules.dominio_3.Pagos.routers import router as router_pagos
from app.modules.dominio_3.Pedidos.routers import router as router_pedidos
from app.modules.estadisticas.router import router as router_estadisticas
from app.modules.uploads.routers import router as router_uploads

logger = logging.getLogger(__name__)

# ── Configurar logging para consola ───────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)-25s | %(message)s",
    datefmt="%H:%M:%S",
)

app = FastAPI(title="Food Store")

# ── CORS: debe ser el PRIMER middleware para que envuelva todos los handlers ──
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:5174",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request logging middleware (timing + method + path + status) ──────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Muestra cada peticion en consola con metodo, path, status y duracion."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    status = response.status_code
    # Colorear el status code para visibilidad en consola
    if status < 300:
        color = "\033[92m"  # verde
    elif status < 400:
        color = "\033[94m"  # azul
    elif status < 500:
        color = "\033[93m"  # amarillo
    else:
        color = "\033[91m"  # rojo

    logger.info(
        "%s%s %s\033[0m → %s%d\033[0m  \033[90m(%.1fms)\033[0m",
        color if status >= 400 else "",
        request.method.ljust(6),
        request.url.path,
        color,
        status,
        duration_ms,
    )
    return response

# ── Rate limiting ────────────────────────────────────────────────────────────
app.state.limiter = limiter


async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handler personalizado que loguea el hit antes de devolver 429."""
    client_ip = request.client.host if request.client else "unknown"
    logger.warning(
        "RATE LIMIT HIT | IP: %s | %s %s",
        client_ip,
        request.method,
        request.url.path,
    )
    retry_after = 900  # 15 minutos en segundos
    return JSONResponse(
        status_code=429,
        content={
            "type": "/errors/rate-limit-exceeded",
            "title": "Too Many Requests",
            "status": 429,
            "detail": "Demasiados intentos fallidos. Esperá 15 minutos y volvé a intentar.",
            "code": "RATE_LIMIT_EXCEEDED",
            "instance": str(request.url),
        },
        headers={"Retry-After": str(retry_after)},
    )


app.add_exception_handler(RateLimitExceeded, rate_limit_handler)


# ── Startup ──────────────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    """Crea las tablas si no existen (desarrollo local).
    
    Para entornos productivos, ejecutar manualmente: alembic upgrade head
    """
    create_all_tables()


# ── Static files ─────────────────────────────────────────────────────────────
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ── Exception handler ────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """RFC 7807 — Problem Details for HTTP APIs."""
    logger.exception(
        "Unhandled exception | %s %s | %s: %s",
        request.method,
        request.url.path,
        type(exc).__name__,
        str(exc),
    )
    return JSONResponse(
        status_code=500,
        content={
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": 500,
            "detail": str(exc),
            "instance": str(request.url),
        },
    )


# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(router_auth)
app.include_router(router_categoria)
app.include_router(router_producto)
app.include_router(router_ingrediente)
app.include_router(router_unidad_medida)
app.include_router(router_pedidos)
app.include_router(router_pagos)
app.include_router(router_uploads)
app.include_router(router_estadisticas)


@app.get("/")
def home():
    return {"status": "ok"}
