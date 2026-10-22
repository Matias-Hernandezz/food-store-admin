"""OAuth Mercado Pago por local (credenciales en tenants)."""

from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlmodel import Session, select

from app.control.db import get_control_engine
from app.control.models import Tenant
from app.core.config import settings
from app.core.mercado_pago.token_cipher import decrypt_secret, encrypt_secret

MP_AUTH_URL = "https://auth.mercadopago.com.ar/authorization"
MP_TOKEN_URL = "https://api.mercadopago.com/oauth/token"
_OAUTH_PURPOSE = "mp_oauth_connect"


def _oauth_configured() -> bool:
    return bool(settings.mp_app_id and settings.mp_client_secret and settings.mp_oauth_redirect_uri)


def build_oauth_state(tenant_slug: str) -> str:
    payload = {
        "slug": tenant_slug,
        "purpose": _OAUTH_PURPOSE,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def parse_oauth_state(state: str) -> str:
    try:
        data = jwt.decode(state, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="State inválido") from exc
    if data.get("purpose") != _OAUTH_PURPOSE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="State inválido")
    slug = (data.get("slug") or "").strip().lower()
    if not slug:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="State sin local")
    return slug


def build_authorize_url(tenant_slug: str) -> str:
    if not _oauth_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OAuth de Mercado Pago no configurado en el servidor",
        )
    params = {
        "client_id": settings.mp_app_id,
        "response_type": "code",
        "platform_id": "mp",
        "redirect_uri": settings.mp_oauth_redirect_uri,
        "state": build_oauth_state(tenant_slug),
    }
    return f"{MP_AUTH_URL}?{urlencode(params)}"


async def exchange_authorization_code(code: str) -> dict:
    if not _oauth_configured():
        raise HTTPException(status_code=503, detail="OAuth MP no configurado")
    payload = {
        "client_id": settings.mp_app_id,
        "client_secret": settings.mp_client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.mp_oauth_redirect_uri,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.post(MP_TOKEN_URL, json=payload)
    if res.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pudo obtener token de MP: {res.text[:200]}",
        )
    return res.json()


def save_oauth_tokens(tenant_slug: str, token_response: dict) -> None:
    access = (token_response.get("access_token") or "").strip()
    refresh = (token_response.get("refresh_token") or "").strip()
    if not access:
        raise HTTPException(status_code=400, detail="Respuesta de MP sin access_token")

    expires_in = int(token_response.get("expires_in") or 0)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=max(expires_in, 60))
    public_key = token_response.get("public_key")
    user_id = token_response.get("user_id")

    with Session(get_control_engine()) as session:
        tenant = session.exec(select(Tenant).where(Tenant.slug == tenant_slug)).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Local no encontrado")
        tenant.mp_access_token = encrypt_secret(access)
        tenant.mp_refresh_token = encrypt_secret(refresh) if refresh else None
        tenant.mp_public_key = str(public_key) if public_key else None
        tenant.mp_user_id = str(user_id) if user_id is not None else None
        tenant.mp_token_expires_at = expires_at
        tenant.updated_at = datetime.now(timezone.utc)
        session.add(tenant)
        session.commit()


def mp_connection_status(tenant_slug: str) -> dict:
    with Session(get_control_engine()) as session:
        tenant = session.exec(select(Tenant).where(Tenant.slug == tenant_slug)).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Local no encontrado")
    connected = bool(tenant.mp_access_token)
    return {
        "connected": connected,
        "mp_user_id": tenant.mp_user_id,
        "mp_public_key": tenant.mp_public_key,
        "expires_at": tenant.mp_token_expires_at.isoformat() if tenant.mp_token_expires_at else None,
    }
