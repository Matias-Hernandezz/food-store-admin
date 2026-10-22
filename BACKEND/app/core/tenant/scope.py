"""Contexto de tenant para rutas que resuelven el slug en el path (ej. webhooks MP)."""

from contextlib import contextmanager
from typing import Iterator

from fastapi import HTTPException, status
from sqlmodel import Session

from app.control.db import get_control_engine
from app.control.models import Tenant
from app.core.tenant.context import reset_tenant_context, set_tenant_context
from app.core.tenant.resolver import (
    assert_tenant_active,
    load_tenant_by_slug,
    tenant_database_url,
)


@contextmanager
def tenant_scope(slug: str) -> Iterator[Tenant]:
    slug = slug.strip().lower()
    with Session(get_control_engine()) as control:
        tenant = load_tenant_by_slug(control, slug)
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Local no encontrado",
        )
    try:
        assert_tenant_active(tenant)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    tokens = set_tenant_context(tenant.slug, tenant_database_url(tenant))
    try:
        yield tenant
    finally:
        reset_tenant_context(tokens)
