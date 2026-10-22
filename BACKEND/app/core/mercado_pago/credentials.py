"""Resolución de credenciales Mercado Pago (legacy global o por tenant en control)."""

from dataclasses import dataclass

from sqlmodel import Session, select

from app.control.db import get_control_engine
from app.control.models import Tenant
from app.core.config import settings
from app.core.mercado_pago.token_cipher import decrypt_secret
from app.core.tenant.context import get_current_tenant_slug


@dataclass(frozen=True)
class MpCredentials:
    access_token: str
    webhook_secret: str
    notification_url: str | None


def _secret_for_webhook(access_token: str, webhook_secret: str | None) -> str:
    return (webhook_secret or "").strip() or access_token


def notification_url_for_slug(slug: str | None) -> str | None:
    base = (settings.api_public_base_url or "").strip().rstrip("/")
    if slug and base:
        return f"{base}/webhooks/mp/{slug}"
    legacy = (settings.MP_NOTIFICATION_URL or "").strip()
    return legacy or None


def credentials_from_tenant(tenant: Tenant) -> MpCredentials | None:
    token = decrypt_secret(tenant.mp_access_token).strip()
    if not token:
        return None
    wh_secret = decrypt_secret(tenant.mp_webhook_secret).strip() or None
    return MpCredentials(
        access_token=token,
        webhook_secret=_secret_for_webhook(token, wh_secret),
        notification_url=notification_url_for_slug(tenant.slug),
    )


def load_tenant_mp_credentials(slug: str) -> MpCredentials | None:
    with Session(get_control_engine()) as session:
        tenant = session.exec(select(Tenant).where(Tenant.slug == slug)).first()
    if not tenant:
        return None
    return credentials_from_tenant(tenant)


def get_mp_credentials() -> MpCredentials:
    """
    Legacy: variables de entorno globales.
    Multi: token del tenant activo en context (control DB).
    """
    slug = get_current_tenant_slug()
    if slug:
        creds = load_tenant_mp_credentials(slug)
        if creds:
            return creds

    token = (settings.MP_ACCESS_TOKEN or "").strip()
    if not token:
        raise ValueError("Mercado Pago no configurado para este local")
    wh = (settings.MP_WEBHOOK_SECRET or "").strip() or None
    return MpCredentials(
        access_token=token,
        webhook_secret=_secret_for_webhook(token, wh),
        notification_url=notification_url_for_slug(slug),
    )
