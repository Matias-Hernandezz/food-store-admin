from datetime import date, datetime
from decimal import Decimal

from pydantic import Field, field_validator
from sqlmodel import SQLModel


class ConfigFiscalRead(SQLModel):
    cuit: str
    razon_social: str
    punto_venta: int
    condicion_iva: str
    adapter: str
    habilitado: bool


class ConfigFiscalUpdate(SQLModel):
    cuit: str = Field(min_length=11, max_length=13)
    razon_social: str = Field(min_length=1, max_length=120)
    punto_venta: int = Field(ge=1, le=9999)
    condicion_iva: str = Field(pattern="^(MONOTRIBUTO|RI)$")
    adapter: str = Field(pattern="^(mock|wsfe)$")
    habilitado: bool = False

    @field_validator("cuit", mode="before")
    @classmethod
    def strip_cuit(cls, v: str) -> str:
        return str(v).replace("-", "").strip()


class ComprobanteRead(SQLModel):
    id: int
    pedido_id: int
    tipo_comprobante: int
    numero: int
    cae: str | None
    cae_vencimiento: date | None
    estado: str
    importe_total: Decimal
    qr_payload: str | None
    error_detalle: str | None
    created_at: datetime
