from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import TEXT

def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class FormaPago(SQLModel, table=True):
    __tablename__ = "forma_pago"

    codigo:      str           = Field(primary_key=True, max_length=20)
    descripcion: str           = Field(max_length=80)
    habilitado:  bool          = Field(default=True)

class EstadoPedido(SQLModel, table=True):
    __tablename__ = "estado_pedido"

    codigo:       str           = Field(primary_key=True, max_length=20)
    descripcion:  str           = Field(max_length=80)
    orden:        int           = Field()       # para ordenar en UI
    es_terminal:  bool          = Field(default=False)

class Pedido(SQLModel, table=True):
    __tablename__ = "pedido"

    id:              Optional[int] = Field(default=None, primary_key=True)

    usuario_id:      int           = Field(foreign_key="usuario.id")
    direccion_id:    Optional[int] = Field(default=None, foreign_key="direccion_entrega.id")
    estado_codigo:   str           = Field(foreign_key="estado_pedido.codigo", default="PENDIENTE")
    forma_pago_codigo: str         = Field(foreign_key="forma_pago.codigo")
    subtotal:        Decimal       = Field(decimal_places=2, max_digits=10)
    descuento:       Decimal       = Field(default=Decimal("0.00"), decimal_places=2, max_digits=10)
    costo_envio:     Decimal       = Field(default=Decimal("0.00"), decimal_places=2, max_digits=10)
    total:           Decimal       = Field(decimal_places=2, max_digits=10)
    notas:           Optional[str] = Field(default=None, sa_column=Column(TEXT))
    created_at:      datetime      = Field(default_factory=now_utc)
    updated_at:      datetime      = Field(default_factory=now_utc)
    deleted_at:      Optional[datetime] = Field(default=None)

    detalles:  List["DetallePedido"]        = Relationship(back_populates="pedido")
    historial: List["HistorialEstadoPedido"] = Relationship(back_populates="pedido")

class HistorialEstadoPedido(SQLModel, table=True):
    __tablename__ = "historial_estado_pedido"
    id:           Optional[int] = Field(default=None, primary_key=True)
    pedido_id:    int           = Field(foreign_key="pedido.id", index=True)
    estado_desde: Optional[str] = Field(default=None, foreign_key="estado_pedido.codigo")
    estado_hacia: str           = Field(foreign_key="estado_pedido.codigo")
    usuario_id:   Optional[int] = Field(default=None, foreign_key="usuario.id")
    motivo:       Optional[str] = Field(default=None, sa_column=Column(TEXT))
  
    created_at:   datetime      = Field(default_factory=now_utc)
    pedido: Pedido = Relationship(back_populates="historial")


class DetallePedido(SQLModel, table=True):
    __tablename__ = "detalle_pedido"

    pedido_id:        int     = Field(foreign_key="pedido.id",   primary_key=True)
    producto_id:      int     = Field(foreign_key="producto.id", primary_key=True)
    cantidad:         int     = Field(ge=1)
    nombre_snapshot:  str     = Field(max_length=200)
    precio_snapshot:  Decimal = Field(decimal_places=2, max_digits=10, ge=Decimal("0"))
    subtotal:         Decimal = Field(decimal_places=2, max_digits=10, ge=Decimal("0"))
    personalizacion:  Optional[int] = Field(default=None)

    # Audit
    created_at:       datetime = Field(default_factory=now_utc)

    # Relación
    pedido: Pedido = Relationship(back_populates="detalles")
