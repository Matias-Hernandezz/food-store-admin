from datetime import datetime
from decimal import Decimal
from pydantic import field_validator
from sqlmodel import SQLModel


class CrearPagoInput(SQLModel):
    """Lo que manda el frontend después de que el Brick tokeniza la tarjeta."""
    pedido_id: int
    token: str
    payment_method_id: str
    installments: int = 1
    issuer_id: str | None = None
    dni_number: str | None = None

    @field_validator("installments")
    @classmethod
    def cuotas_validas(cls, v: int) -> int:
        if v < 1 or v > 12:
            raise ValueError("installments debe estar entre 1 y 12")
        return v


class MPWebhookPayload(SQLModel):
    """Payload que manda MercadoPago al webhook IPN."""
    action: str | None = None
    api_version: str | None = None
    data: dict | None = None
    date_created: str | None = None
    id: int | None = None
    live_mode: bool | None = None
    type: str | None = None
    user_id: int | None = None


class PagoResponse(SQLModel):
    id: int
    pedido_id: int
    mp_payment_id: int | None
    mp_status: str
    mp_status_detail: str | None
    transaction_amount: Decimal
    payment_method_id: str | None
    external_reference: str
    created_at: datetime
    updated_at: datetime


class WebhookResponse(SQLModel):
    status: str = "ok"
    message: str = "Notificación procesada"
