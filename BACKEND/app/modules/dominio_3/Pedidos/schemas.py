
from app.modules.dominio_1.Usuarios.schemas import DireccionRead
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
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
    personalizacion: List[int] = Field(default_factory=list)

class DetallePedidoRead(SQLModel):
    producto_id:     int
    cantidad:        int
    nombre_snapshot: str
    precio_snapshot: Decimal
    subtotal:        Decimal
    personalizacion: List[int] = Field(default_factory=list)

class PedidoCreate(SQLModel):
    direccion_id:   Optional[int] = None
    forma_pago_codigo: str
    notas:             Optional[str] = None
    items:             List[ItemCarritoInput]

class PedidoRead(SQLModel):
    id:                int
    usuario_id:        int
    usuario_nombre:    Optional[str] = None
    direccion_id:      Optional[int]
    estado_codigo:     str
    forma_pago_codigo: str
    subtotal:          Decimal
    descuento:         Decimal
    costo_envio:       Decimal
    total:             Decimal
    notas:             Optional[str]
    created_at:        datetime
    detalles:          List[DetallePedidoRead] = []
    direccion:         Optional[DireccionRead] = None
    pago:              Optional["PagoRead"] = None
class PedidoList(SQLModel):
    data:  List[PedidoRead]
    total: int

class HistorialRead(SQLModel):
    id:           int
    estado_desde: Optional[str]
    estado_hacia: str
    usuario_id:   Optional[int]
    motivo:       Optional[str]
    created_at:   datetime

class AvanzarEstadoInput(SQLModel):
    nuevo_estado: str
    motivo: Optional[str] = None
class AvanzarEstadoResult(SQLModel):
    pedido: PedidoRead
    estado_anterior: Optional[str]

class PagoRead(SQLModel):
    """Versión resumida del pago para incluir en PedidoRead."""
    id: int
    mp_payment_id: Optional[int]
    mp_status: str
    mp_status_detail: Optional[str]
    transaction_amount: Decimal
    payment_method_id: Optional[str]
    external_reference: str
    created_at: datetime
