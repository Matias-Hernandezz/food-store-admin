import re

from fastapi import Request
from sqlmodel import Session, select

from app.control.models import Tenant, TenantDomain, TenantStatus
from app.core.config import settings

_HOST_RE = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$", re.I)


def _normalize_host(host: str) -> str:
    host = host.split(":")[0].strip().lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def resolve_slug_from_request(request: Request) -> str | None:
    header = request.headers.get("x-tenant-slug", "").strip().lower()
    if header:
        return header if _HOST_RE.match(header) else None

    host = _normalize_host(request.headers.get("host", ""))
    if not host:
        return None

    base = settings.tenant_base_domain.strip().lower()
    if base and host.endswith(f".{base}") and host != base:
        sub = host[: -(len(base) + 1)]
        if sub and "." not in sub and _HOST_RE.match(sub):
            return sub.lower()

    return None


def tenant_database_url(tenant: Tenant) -> str:
    user = tenant.db_user or settings.postgres_user
    password = tenant.db_password if tenant.db_password is not None else settings.postgres_password
    return (
        f"postgresql://{user}:{password}"
        f"@{settings.postgres_host}:{settings.postgres_port}/{tenant.db_name}"
    )


def load_tenant_by_slug(session: Session, slug: str) -> Tenant | None:
    return session.exec(select(Tenant).where(Tenant.slug == slug)).first()


def load_tenant_by_host(session: Session, host: str) -> Tenant | None:
    host = _normalize_host(host)
    row = session.exec(select(TenantDomain).where(TenantDomain.host == host)).first()
    if not row:
        return None
    return session.get(Tenant, row.tenant_id)


def assert_tenant_active(tenant: Tenant) -> None:
    if tenant.estado != TenantStatus.ACTIVE.value:
        raise ValueError(f"Tenant {tenant.slug} no está activo ({tenant.estado})")
