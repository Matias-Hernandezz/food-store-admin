import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.control.db import get_control_engine
from app.core.config import settings
from app.core.tenant.context import reset_tenant_context, set_tenant_context
from app.core.tenant.resolver import (
    assert_tenant_active,
    load_tenant_by_host,
    load_tenant_by_slug,
    resolve_slug_from_request,
    tenant_database_url,
)

logger = logging.getLogger(__name__)

_SKIP_PREFIXES = (
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/uploads/",
    "/webhooks/",
    "/api/v1/integrations/mp/callback",
)


async def tenant_context_middleware(request: Request, call_next):
    if settings.tenant_mode != "multi":
        return await call_next(request)

    path = request.url.path
    if path == "/" or any(path.startswith(p) for p in _SKIP_PREFIXES):
        return await call_next(request)

    slug = resolve_slug_from_request(request)
    host = request.headers.get("host", "")

    with Session(get_control_engine()) as control:
        tenant = None
        if slug:
            tenant = load_tenant_by_slug(control, slug)
        if tenant is None and host:
            tenant = load_tenant_by_host(control, host)
        if tenant is None and settings.default_tenant_slug:
            tenant = load_tenant_by_slug(control, settings.default_tenant_slug)

    if tenant is None:
        return JSONResponse(
            status_code=404,
            content={
                "type": "about:blank",
                "title": "Local no encontrado",
                "status": 404,
                "detail": "No se pudo resolver el tenant para esta petición.",
            },
        )

    try:
        assert_tenant_active(tenant)
    except ValueError as exc:
        return JSONResponse(
            status_code=403,
            content={
                "type": "about:blank",
                "title": "Local no disponible",
                "status": 403,
                "detail": str(exc),
            },
        )

    db_url = tenant_database_url(tenant)
    tokens = set_tenant_context(tenant.slug, db_url)
    request.state.tenant_slug = tenant.slug

    try:
        return await call_next(request)
    finally:
        reset_tenant_context(tokens)
