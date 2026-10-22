from decimal import Decimal

from sqlmodel import Session, select

from app.control.db import get_control_engine
from app.control.models import Tenant
from app.core.config import settings
from app.core.tenant.context import get_current_tenant_slug


def delivery_app_fee_percent_for_tenant(slug: str | None = None) -> Decimal:
    """% de comisión delivery usado en el KPI de ahorro (por tenant o default)."""
    resolved = (slug or get_current_tenant_slug() or settings.default_tenant_slug or "").strip().lower()
    default = Decimal(str(settings.default_delivery_app_fee_percent)).quantize(Decimal("0.01"))

    if settings.tenant_mode != "multi" or not resolved:
        return default

    with Session(get_control_engine()) as session:
        tenant = session.exec(select(Tenant).where(Tenant.slug == resolved)).first()
    if not tenant or tenant.delivery_app_fee_percent is None:
        return default
    return Decimal(str(tenant.delivery_app_fee_percent)).quantize(Decimal("0.01"))
