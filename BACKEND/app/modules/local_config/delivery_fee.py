from decimal import Decimal

from fastapi import HTTPException
from sqlmodel import Session, select

from app.control.db import get_control_engine
from app.control.models import Tenant
from app.core.config import settings
from app.core.tenant.context import get_current_tenant_slug
from app.core.tenant.settings import delivery_app_fee_percent_for_tenant


def get_delivery_fee_admin() -> dict:
    pct = delivery_app_fee_percent_for_tenant()
    slug = (get_current_tenant_slug() or settings.default_tenant_slug or "").strip().lower()
    return {
        "delivery_app_fee_percent": float(pct),
        "usa_default_global": settings.tenant_mode != "multi" or not slug,
        "tenant_slug": slug or None,
    }


def set_delivery_fee_admin(percent: Decimal) -> dict:
    if percent < Decimal("0") or percent > Decimal("100"):
        raise ValueError("El porcentaje debe estar entre 0 y 100")

    slug = (get_current_tenant_slug() or settings.default_tenant_slug or "").strip().lower()
    if settings.tenant_mode != "multi" or not slug:
        raise HTTPException(
            status_code=400,
            detail="En modo single-tenant usá DEFAULT_DELIVERY_APP_FEE_PERCENT en el servidor",
        )

    with Session(get_control_engine()) as session:
        tenant = session.exec(select(Tenant).where(Tenant.slug == slug)).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Local no encontrado")
        tenant.delivery_app_fee_percent = percent.quantize(Decimal("0.01"))
        session.add(tenant)
        session.commit()

    return get_delivery_fee_admin()
