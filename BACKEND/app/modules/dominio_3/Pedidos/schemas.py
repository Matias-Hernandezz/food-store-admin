from app.modules.dominio_1.direcciones.schemas import DireccionRead
from datetime import datetime
from decimal import Decimal
from pydantic import field_validator
from sqlmodel import Field
from sqlmodel import SQLModel


class FormaPagoRead(SQLModel):
    codigo:      str
    descripcion: str
    habilitado:  bool


class EstadoPedidoRead(SQLModel):
    codigo:      str
    descripcion: str
    orden:       int
    es_terminal: bool


class ItemCarritoInput(SQLModel):
    producto_id:     int
    cantidad:        int = Field(ge=1)
    personalizacion: list[int] = Field(default_factory=list)


class DetallePedidoRead(SQLModel):
    producto_id:     int
    cantidad:        int
    nombre_snapshot: str
    precio_snapshot: Decimal
    subtotal:        Decimal
    personalizacion: list[int] = Field(default_factory=list)


class PedidoCreate(SQLModel):
    direccion_id:      int | None = None
    forma_pago_codigo: str
    notas:             str | None = None
    items:             list[ItemCarritoInput]


class PedidoRead(SQLModel):
    id:                int
    usuario_id:        int
    usuario_nombre:    str | None = None
    direccion_id:      int | None
    estado_codigo:     str
    forma_pago_codigo: str
    subtotal:          Decimal
    descuento:         Decimal
    costo_envio:       Decimal
    total:             Decimal
    notas:             str | None
    created_at:        datetime
    detalles:          list[DetallePedidoRead] = []
    direccion:         DireccionRead | None = None
    pago:              "PagoRead | None" = None


class PedidoList(SQLModel):
    data:  list[PedidoRead]
    total: int


class HistorialRead(SQLModel):
    id:           int
    estado_desde: str | None
    estado_hacia: str
    usuario_id:   int | None
    motivo:       str | None
    created_at:   datetime


class AvanzarEstadoInput(SQLModel):
    nuevo_estado: str
    motivo: str | None = None

    @field_validator("nuevo_estado", mode="before")
    @classmethod
    def normalizar_estado(cls, v: str) -> str:
        """Normaliza el código de estado a mayúsculas (ej: 'pendiente' → 'PENDIENTE')."""
        return v.upper() if isinstance(v, str) else v


class AvanzarEstadoResult(SQLModel):
    pedido: PedidoRead
    estado_anterior: str | None


class PagoRead(SQLModel):
    """Versión resumida del pago para incluir en PedidoRead."""
    id: int
    mp_payment_id: int | None
    mp_status: str
    mp_status_detail: str | None
    transaction_amount: Decimal
    payment_method_id: str | None
    external_reference: str
    created_at: datetime
