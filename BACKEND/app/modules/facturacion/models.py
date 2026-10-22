from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Numeric, Text, UniqueConstraint
from sqlmodel import Field, SQLModel


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class ConfigFiscal(SQLModel, table=True):
    __tablename__ = "config_fiscal"

    id: Optional[int] = Field(default=None, primary_key=True)
    cuit: str = Field(max_length=11, default="00000000000")
    razon_social: str = Field(max_length=120, default="Local")
    punto_venta: int = Field(default=1)
    condicion_iva: str = Field(max_length=20, default="MONOTRIBUTO")
    adapter: str = Field(max_length=32, default="mock")
    habilitado: bool = Field(default=False)


class ComprobanteFiscal(SQLModel, table=True):
    __tablename__ = "comprobante_fiscal"
    __table_args__ = (UniqueConstraint("pedido_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id", index=True)
    tipo_comprobante: int = Field(default=11)
    numero: int
    cae: Optional[str] = Field(default=None, max_length=14)
    cae_vencimiento: Optional[date] = Field(default=None)
    estado: str = Field(max_length=20, default="PENDIENTE_CAE")
    importe_total: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    qr_payload: Optional[str] = Field(default=None, sa_column=Column(Text))
    error_detalle: Optional[str] = Field(default=None, sa_column=Column(Text))
    idempotency_key: str = Field(max_length=64, unique=True)
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)
