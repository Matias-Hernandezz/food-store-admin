import logging
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

import mercadopago
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

from app.core.config import settings
from app.modules.dominio_3.Pagos.models import Pago
from app.modules.dominio_3.Pagos.schemas import (
    CrearPagoInput,
    PagoResponse,
    MPWebhookPayload,
)
from app.modules.dominio_3.Pagos.unit_of_work import PagoUnitOfWork
from app.modules.dominio_3.Pedidos.models import HistorialEstadoPedido




ESTADOS_TERMINALES_PAGO = {"approved", "rejected", "cancelled", "refunded", "charged_back"}
ESTADO_PEDIDO_TRAS_PAGO = "CONFIRMADO"




class CrearPagoResult:
    """Lo que devuelve crear_pago() al router."""
    def __init__(self, pago: PagoResponse, pedido_confirmado: bool):
        self.pago = pago
        self.pedido_confirmado = pedido_confirmado


class WebhookResult:
    """Lo que devuelve procesar_webhook() al router."""
    def __init__(
        self,
        status: str,
        message: str,
        pedido_confirmado: bool = False,
        pedido_id: Optional[int] = None,
        payment_method_id: Optional[str] = None,
        transaction_amount: float = 0.0,
    ):
        self.status = status
        self.message = message
        self.pedido_confirmado = pedido_confirmado
        self.pedido_id = pedido_id
        self.payment_method_id = payment_method_id
        self.transaction_amount = transaction_amount




class PagoService:
    def __init__(self, uow: PagoUnitOfWork):
        self.uow = uow


    def crear_pago(
        self,
        data: CrearPagoInput,
        usuario_id: int,
        email_usuario: str,
    ) -> CrearPagoResult:
        """
        Flujo completo de creación de pago con MercadoPago.
        El router se encarga del broadcast WS post-commit.
        """

        pedido = self.uow.pedidos.get_by_id_con_detalles(data.pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )
        if pedido.usuario_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No podés pagar un pedido de otro usuario",
            )
        if pedido.estado_codigo != "PENDIENTE":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El pedido está en estado '{pedido.estado_codigo}' — solo se puede pagar un pedido PENDIENTE",
            )

        # Idempotency check: key derivada del pedido_id — evita cobros duplicados
        # La DB unique constraint sobre idempotency_key protege contra race conditions
        idempotency_key = f"pay_{data.pedido_id}"

        pago_duplicado = self.uow.pagos.get_by_idempotency_key(idempotency_key)
        if pago_duplicado:
            return CrearPagoResult(
                pago=self._to_response(pago_duplicado),
                pedido_confirmado=(pago_duplicado.mp_status == "approved"),
            )

        # Check if pedido already has a non-rejected payment
        pago_existente = self.uow.pagos.get_by_pedido_id(pedido.id)
        if pago_existente and pago_existente.mp_status not in ("rejected",):
            return CrearPagoResult(
                pago=self._to_response(pago_existente),
                pedido_confirmado=(pago_existente.mp_status == "approved"),
            )

        external_reference = f"pedido_{pedido.id}_{uuid.uuid4().hex[:8]}"

        pago = Pago(
            pedido_id=pedido.id,
            mp_status="pending",
            transaction_amount=pedido.total,
            external_reference=external_reference,
            idempotency_key=idempotency_key,
        )
        pago = self.uow.pagos.add(pago)

        sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)

        payment_data = {
            "transaction_amount": float(pedido.total),
            "token": data.token,
            "description": f"Food Store - Pedido #{pedido.id}",
            "installments": data.installments,
            "payment_method_id": data.payment_method_id,
            "issuer_id": data.issuer_id,
            "payer": {
                "email": email_usuario,
                "identification": {
                    "type": "DNI",
                    "number": data.dni_number or "",
                },
            } if data.dni_number else {
                "email": email_usuario,
            },
            "external_reference": external_reference,
            "notification_url": settings.MP_NOTIFICATION_URL or None,
            "binary_mode": True,
        }

        try:
            mp_result = sdk.payment().create(payment_data)
        except Exception as e:
            pago.mp_status = "error"
            pago.mp_status_detail = f"Error SDK: {str(e)[:90]}"
            self.uow.pagos.update(pago)
            return CrearPagoResult(pago=self._to_response(pago), pedido_confirmado=False)

        mp_response = mp_result.get("response", {})
        mp_status_code = mp_result.get("status", 500)

        if mp_status_code in (200, 201):
            mp_payment_id = mp_response.get("id")
            mp_status = mp_response.get("status", "pending")
            mp_status_detail = mp_response.get("status_detail", "")
            payment_method_id = mp_response.get("payment_method_id", data.payment_method_id)
            transaction_amount = Decimal(str(mp_response.get("transaction_amount", pedido.total)))

            pago.mp_payment_id = mp_payment_id
            pago.mp_status = mp_status
            pago.mp_status_detail = mp_status_detail
            pago.payment_method_id = payment_method_id
            pago.transaction_amount = transaction_amount
            pago.updated_at = datetime.now(timezone.utc)
            self.uow.pagos.update(pago)

            pedido_confirmado = False
            if mp_status == "approved":
                self._confirmar_pedido(pedido, usuario_id)
                pedido_confirmado = True

            return CrearPagoResult(
                pago=self._to_response(pago),
                pedido_confirmado=pedido_confirmado,
            )
        else:
            pago.mp_status = "rejected"
            pago.mp_status_detail = mp_response.get("message", "Error desconocido")[:100]
            pago.updated_at = datetime.now(timezone.utc)
            self.uow.pagos.update(pago)
            return CrearPagoResult(pago=self._to_response(pago), pedido_confirmado=False)


    def procesar_webhook(self, payload: MPWebhookPayload) -> WebhookResult:
        """
        Endpoint IPN de MercadoPago.
        MP notifica cuando un pago cambia de estado (ej: pending → approved).
        El router se encarga del broadcast WS post-commit.
        """
        if payload.type != "payment":
            return WebhookResult(status="ignored", message="No es notificación de pago")

        mp_payment_id = payload.data.get("id") if payload.data else None
        if not mp_payment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Notificación sin payment_id",
            )

        pago = self.uow.pagos.get_by_mp_payment_id(int(mp_payment_id))
        if not pago:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pago con mp_payment_id={mp_payment_id} no encontrado",
            )

        if pago.mp_status in ESTADOS_TERMINALES_PAGO:
            return WebhookResult(
                status="ok",
                message=f"Pago ya en estado terminal: {pago.mp_status}",
            )

        sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
        try:
            mp_result = sdk.payment().get(int(mp_payment_id))
            mp_response = mp_result.get("response", {})
            nuevo_estado = mp_response.get("status", pago.mp_status)
        except Exception:
            nuevo_estado = pago.mp_status

        pago.mp_status = nuevo_estado
        pago.mp_status_detail = mp_response.get("status_detail", pago.mp_status_detail)
        pago.transaction_amount = Decimal(
            str(mp_response.get("transaction_amount", pago.transaction_amount))
        )
        pago.payment_method_id = mp_response.get(
            "payment_method_id", pago.payment_method_id
        )
        pago.updated_at = datetime.now(timezone.utc)
        self.uow.pagos.update(pago)

        pedido_confirmado = False
        pedido = self.uow.pedidos.get_by_id_con_detalles(pago.pedido_id)
        if nuevo_estado == "approved" and pedido and pedido.estado_codigo == "PENDIENTE":
            self._confirmar_pedido(pedido, usuario_id=None)
            pedido_confirmado = True

        return WebhookResult(
            status="ok",
            message=f"Pago actualizado a: {nuevo_estado}",
            pedido_confirmado=pedido_confirmado,
            pedido_id=pago.pedido_id,
            payment_method_id=pago.payment_method_id,
            transaction_amount=float(pago.transaction_amount),
        )



    def consultar_pago(self, pedido_id: int, usuario_id: int, es_admin: bool) -> PagoResponse:
        pedido = self.uow.pedidos.get_by_id_con_detalles(pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )

        if not es_admin and pedido.usuario_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tenés acceso al pago de este pedido",
            )

        pago = self.uow.pagos.get_by_pedido_id(pedido_id)
        if not pago:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay pago registrado para este pedido",
            )

        if pago.mp_status not in ESTADOS_TERMINALES_PAGO and pago.mp_payment_id:
            pago = self._sincronizar_desde_mp(pago)

        return self._to_response(pago)



    def _confirmar_pedido(self, pedido, usuario_id: Optional[int]) -> None:
        """Avanza el pedido de PENDIENTE a CONFIRMADO + registro en historial."""
        estado_anterior = pedido.estado_codigo
        pedido.estado_codigo = ESTADO_PEDIDO_TRAS_PAGO
        pedido.updated_at = datetime.now(timezone.utc)
        self.uow.pedidos.update(pedido)

        self.uow.historial.add(
            HistorialEstadoPedido(
                pedido_id=pedido.id,
                estado_desde=estado_anterior,
                estado_hacia=ESTADO_PEDIDO_TRAS_PAGO,
                usuario_id=usuario_id,
                motivo="Pago aprobado por MercadoPago",
            )
        )

    def _sincronizar_desde_mp(self, pago: Pago) -> Pago:
        """Consulta a MP y actualiza el registro local si cambió el estado."""
        sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
        try:
            mp_result = sdk.payment().get(int(pago.mp_payment_id))
            mp_response = mp_result.get("response", {})
            nuevo_estado = mp_response.get("status")

            if nuevo_estado and nuevo_estado != pago.mp_status:
                pago.mp_status = nuevo_estado
                pago.mp_status_detail = mp_response.get("status_detail", "")
                pago.updated_at = datetime.now(timezone.utc)
                self.uow.pagos.update(pago)
                # ✅ No llamar commit() acá — el UoW hace commit en __exit__
        except Exception:
            logger.warning(
                "No se pudo sincronizar pago %s con MercadoPago",
                pago.mp_payment_id,
                exc_info=True,
            )

        return pago



    ROLES_NOTIFICACION = ["ADMIN", "PEDIDOS", "CLIENT"]

    @staticmethod
    async def emitir_ws_pago_aprobado(pedido_id: int, payment_method_id: str | None, transaction_amount: float) -> None:
        """
        Emite evento WS cuando un pago es aprobado.
        Se llama DESDE EL ROUTER, fuera del bloque UoW (RN-06).
        """
        from app.core.ws_manager import ws_manager

        payload = ws_manager.make_event(
            event="pago_confirmado",
            pedido_id=pedido_id,
            estado_anterior="PENDIENTE",
            estado_nuevo=ESTADO_PEDIDO_TRAS_PAGO,
            usuario_id=None,
            motivo="Pago aprobado por MercadoPago",
            data={
                "payment_method_id": payment_method_id,
                "transaction_amount": transaction_amount,
            },
        )

        await ws_manager.broadcast_pedido(
            pedido_id=pedido_id,
            roles=PagoService.ROLES_NOTIFICACION,
            payload=payload,
        )



    @staticmethod
    def _to_response(pago: Pago) -> PagoResponse:
        return PagoResponse(
            id=pago.id,
            pedido_id=pago.pedido_id,
            mp_payment_id=pago.mp_payment_id,
            mp_status=pago.mp_status,
            mp_status_detail=pago.mp_status_detail,
            transaction_amount=pago.transaction_amount,
            payment_method_id=pago.payment_method_id,
            external_reference=pago.external_reference,
            created_at=pago.created_at,
            updated_at=pago.updated_at,
        )