from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, BigInteger

if TYPE_CHECKING:
    from app.modules.dominio_3.pedidos.models import Pedido


def now_utc()->datetime:
    return datetime.now(timezone.utc)


class Pago(SQLModel, table=True):
    __tablename__ = "pago"

    id: Optional[int] = Field(default=None, primary_key=True)

    pedido_id: int = Field(
        foreign_key="pedido.id",
        index=True,
        nullable=False,
    )

    mp_payment_id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, unique=True, nullable=True),
    )
    mp_status: str = Field(
        default="pending",
        max_length=30,
        nullable=False,
    )
    mp_status_detail: Optional[str] = Field(
        default=None,
        max_length=100,
    )
    transaction_amount: Decimal = Field(
        decimal_places=2,
        max_digits=10,
        nullable=False,
    )
    payment_method_id: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    external_reference: str = Field(
        max_length=100,
        unique=True,
        nullable=False,
        index=True,
    )
    idempotency_key: str = Field(
        max_length=100,
        unique=True,
        nullable=False,
        index=True,
    )

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)

    pedido: Optional["Pedido"] = Relationship(back_populates="pago")