import logging
from typing import Annotated, Generator

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlmodel import Session

logger = logging.getLogger(__name__)

from app.core.db import get_session
from app.core.deps import get_active_user, require_role
from app.modules.dominio_1.usuarios.models import Usuario
from app.modules.dominio_3.pagos.schemas import (
    CrearPagoInput,
    MPWebhookPayload,
    PagoResponse,
    WebhookResponse,
)
from app.modules.dominio_3.pagos.services import PagoService
from app.modules.dominio_3.pagos.unit_of_work import PagoUnitOfWork

router = APIRouter(prefix="/api/v1/pagos", tags=["Pagos"])


def get_pago_uow(
    session: Session = Depends(get_session),
) -> Generator[PagoUnitOfWork, None, None]:
    with PagoUnitOfWork(session) as uow:
        yield uow


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "/crear",
    response_model=PagoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un pago con MercadoPago",
    dependencies=[Depends(require_role(["CLIENT"]))],
)
async def crear_pago(
    data: CrearPagoInput,
    current_user: Annotated[Usuario, Depends(get_active_user)],
    uow: PagoUnitOfWork = Depends(get_pago_uow),
):
    """
    PCI SAQ-A: el frontend tokeniza la tarjeta con el Brick de MP.
    Los datos de tarjeta NUNCA tocan nuestro backend.
    """
    with uow:
        result = PagoService(uow).crear_pago(
            data=data,
            usuario_id=current_user.id,
            email_usuario=current_user.email,
        )

    if result.pedido_confirmado:
        await PagoService.emitir_ws_pago_aprobado(
            pedido_id=data.pedido_id,
            payment_method_id=result.pago.payment_method_id,
            transaction_amount=float(result.pago.transaction_amount),
        )

    return result.pago


@router.post(
    "/webhook",
    response_model=WebhookResponse,
    summary="Webhook IPN de MercadoPago — validación de firma HMAC",
)
async def webhook_mercadopago(
    payload: MPWebhookPayload,
    request: Request,
    x_signature: Annotated[str | None, Header()] = None,
    x_request_id: Annotated[str | None, Header(alias="x-request-id")] = None,
    uow: PagoUnitOfWork = Depends(get_pago_uow),
):
    """
    MercadoPago notifica asíncronamente cambios de estado del pago.
    La firma HMAC-SHA256 se valida con el header x-signature.
    Si se aprueba, avanza el pedido a CONFIRMADO y emite WS.
    """
    # Validar firma del webhook (EST-03 compliance)
    mp_payment_id = payload.data.get("id") if payload.data else None
    if mp_payment_id and not PagoService.verificar_firma_mp(
        int(mp_payment_id), x_signature, x_request_id
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firma del webhook inválida",
        )

    with uow:
        result = PagoService(uow).procesar_webhook(payload)

    if result.pedido_confirmado and result.pedido_id:
        await PagoService.emitir_ws_pago_aprobado(
            pedido_id=result.pedido_id,
            payment_method_id=result.payment_method_id,
            transaction_amount=result.transaction_amount,
        )

    return {"status": result.status, "message": result.message}


@router.get(
    "/{pedido_id}",
    response_model=PagoResponse,
    summary="Consultar el pago de un pedido",
    dependencies=[Depends(require_role(["ADMIN", "PEDIDOS", "CLIENT"]))],
)
def consultar_pago(
    pedido_id: int,
    current_user: Annotated[Usuario, Depends(get_active_user)],
    uow: PagoUnitOfWork = Depends(get_pago_uow),
):
    with uow:
        return PagoService(uow).consultar_pago(
            pedido_id=pedido_id,
            usuario_id=current_user.id,
            roles_usuario=[rol.codigo for rol in current_user.roles],
        )
