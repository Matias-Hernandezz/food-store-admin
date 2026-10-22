import logging
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Request, status

from app.core.db import get_session
from app.core.mercado_pago.credentials import load_tenant_mp_credentials
from app.core.tenant.scope import tenant_scope
from app.modules.dominio_3.pagos.schemas import MPWebhookPayload, WebhookResponse
from app.modules.dominio_3.pagos.services import PagoService
from app.modules.dominio_3.pagos.unit_of_work import PagoUnitOfWork

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/mp", tags=["Webhooks Mercado Pago"])


@router.post(
    "/{slug}",
    response_model=WebhookResponse,
    summary="Webhook IPN de Mercado Pago por local",
)
async def webhook_mercadopago_por_local(
    request: Request,
    slug: str,
    payload: MPWebhookPayload,
    x_signature: Annotated[str | None, Header()] = None,
    x_request_id: Annotated[str | None, Header(alias="x-request-id")] = None,
):
    """
    URL recomendada en MP: {API_PUBLIC_BASE_URL}/webhooks/mp/{slug}
    Usa el access token y secret del tenant en la DB de control.
    """
    creds = load_tenant_mp_credentials(slug)
    if creds is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mercado Pago no configurado para este local",
        )

    if payload.type == "payment":
        mp_payment_id = payload.data.get("id") if payload.data else None
        if not mp_payment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Notificación de pago sin id",
            )
        if not PagoService.verificar_firma_mp(
            int(mp_payment_id),
            x_signature,
            x_request_id,
            webhook_secret=creds.webhook_secret,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firma del webhook inválida",
            )

    with tenant_scope(slug):
        session_provider = request.app.dependency_overrides.get(get_session, get_session)
        gen = session_provider()
        session = next(gen)
        try:
            with PagoUnitOfWork(session) as uow:
                result = PagoService(uow).procesar_webhook(payload)
        finally:
            gen.close()

        if result.pedido_confirmado and result.pedido_id:
            await PagoService.emitir_ws_pago_aprobado(
                pedido_id=result.pedido_id,
                payment_method_id=result.payment_method_id,
                transaction_amount=result.transaction_amount,
            )

    return {"status": result.status, "message": result.message}
