from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import field_validator
from sqlmodel import SQLModel


class CrearPagoInput(SQLModel):
    """Lo que manda el frontend después de que el Brick tokeniza la tarjeta."""
    pedido_id: int
    token: str
    payment_method_id: str
    installments: int = 1
    issuer_id: Optional[str] = None
    dni_number: Optional[str] = None

    @field_validator("installments")
    @classmethod
    def cuotas_validas(cls, v: int) -> int:
        if v < 1 or v > 12:
            raise ValueError("installments debe estar entre 1 y 12")
        return v


class MPWebhookPayload(SQLModel):
    """Payload que manda MercadoPago al webhook IPN."""
    action: Optional[str] = None
    api_version: Optional[str] = None
    data: Optional[dict] = None
    date_created: Optional[str] = None
    id: Optional[int] = None
    live_mode: Optional[bool] = None
    type: Optional[str] = None
    user_id: Optional[int] = None


class PagoResponse(SQLModel):
    id: int
    pedido_id: int
    mp_payment_id: Optional[int]
    mp_status: str
    mp_status_detail: Optional[str]
    transaction_amount: Decimal
    payment_method_id: Optional[str]
    external_reference: str
    created_at: datetime
    updated_at: datetime


class WebhookResponse(SQLModel):
    status: str = "ok"
    message: str = "Notificación procesada"
