from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from starlette.requests import Request

from app.core.deps import get_active_user, require_role
from app.core.mercado_pago.oauth import (
    build_authorize_url,
    exchange_authorization_code,
    mp_connection_status,
    parse_oauth_state,
    save_oauth_tokens,
)
from app.core.tenant.context import get_current_tenant_slug
from app.modules.dominio_1.usuarios.models import Usuario
from app.core.config import settings

router = APIRouter(prefix="/api/v1/integrations/mp", tags=["Integraciones — Mercado Pago"])


def _resolve_slug(request: Request, slug: str | None = None) -> str:
    resolved = get_current_tenant_slug() or (slug or "").strip().lower()
    if not resolved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Indicá el local (header X-Tenant-Slug o ?slug=)",
        )
    return resolved


@router.get(
    "/status",
    dependencies=[Depends(require_role(["OWNER"]))],
)
def mp_status(
    _user: Annotated[Usuario, Depends(get_active_user)],
    request: Request,
    slug: Annotated[str | None, Query()] = None,
):
    return mp_connection_status(_resolve_slug(request, slug))


@router.get(
    "/authorize-url",
    dependencies=[Depends(require_role(["OWNER"]))],
)
def mp_authorize_url(
    _user: Annotated[Usuario, Depends(get_active_user)],
    request: Request,
    slug: Annotated[str | None, Query()] = None,
):
    """URL de OAuth para el panel (SPA con Bearer)."""
    tenant_slug = _resolve_slug(request, slug)
    return {"authorize_url": build_authorize_url(tenant_slug)}


@router.get(
    "/authorize",
    dependencies=[Depends(require_role(["OWNER"]))],
)
def mp_authorize(
    _user: Annotated[Usuario, Depends(get_active_user)],
    request: Request,
    slug: Annotated[str | None, Query()] = None,
):
    tenant_slug = _resolve_slug(request, slug)
    return RedirectResponse(build_authorize_url(tenant_slug), status_code=status.HTTP_302_FOUND)


@router.get("/callback")
async def mp_oauth_callback(
    code: Annotated[str | None, Query()] = None,
    state: Annotated[str | None, Query()] = None,
    error: Annotated[str | None, Query()] = None,
):
    """Callback público de Mercado Pago (sin JWT). El slug viaja en `state`."""
    base = (settings.mp_oauth_admin_return_url or "http://localhost:5175").rstrip("/")
    if error:
        return RedirectResponse(
            f"{base}/admin/integraciones?mp=error&reason={error}", status_code=302
        )
    if not code or not state:
        raise HTTPException(status_code=400, detail="Faltan parámetros code o state")

    tenant_slug = parse_oauth_state(state)
    token_response = await exchange_authorization_code(code)
    save_oauth_tokens(tenant_slug, token_response)
    return RedirectResponse(
        f"{base}/admin/integraciones?mp=connected&slug={tenant_slug}", status_code=302
    )
