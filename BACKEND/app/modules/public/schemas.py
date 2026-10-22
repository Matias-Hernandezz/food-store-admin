from datetime import datetime
from decimal import Decimal

from pydantic import EmailStr, Field
from sqlmodel import SQLModel

from app.modules.dominio_1.direcciones.schemas import DireccionCreate
from app.modules.dominio_3.pedidos.schemas import ItemCarritoInput


class PublicProductoRead(SQLModel):
    id: int
    nombre: str
    descripcion: str | None
    precio_base: Decimal
    imagenes_url: list[str] = []
    disponible: bool
    categoria_ids: list[int] = []


class PublicCategoriaRead(SQLModel):
    id: int
    nombre: str
    descripcion: str | None = None
    imagen_url: str | None = None
    parent_id: int | None = None


class PublicCatalogoRead(SQLModel):
    categorias: list[PublicCategoriaRead]
    productos: list[PublicProductoRead]


class PublicTiendaRead(SQLModel):
    abierto: bool
    mensaje: str | None = None


class PublicClienteInput(SQLModel):
    nombre: str = Field(min_length=1, max_length=80)
    apellido: str = Field(min_length=1, max_length=80)
    email: EmailStr
    celular: str | None = Field(default=None, max_length=30)


class PublicPedidoCreate(SQLModel):
    cliente: PublicClienteInput
    items: list[ItemCarritoInput]
    forma_pago_codigo: str
    tipo_pedido: str | None = None
    direccion_id: int | None = None
    direccion: DireccionCreate | None = None
    notas: str | None = None


class PublicPedidoCreated(SQLModel):
    pedido_id: int
    tracking_token: str
    estado_codigo: str
    tipo_pedido: str
    total: Decimal


class PublicDetalleRead(SQLModel):
    cantidad: int
    nombre_snapshot: str
    precio_snapshot: Decimal
    subtotal: Decimal


class PublicSeguimientoRead(SQLModel):
    pedido_id: int
    estado_codigo: str
    tipo_pedido: str
    subtotal: Decimal
    costo_envio: Decimal
    total: Decimal
    created_at: datetime
    updated_at: datetime
    detalles: list[PublicDetalleRead] = []
    ciudad: str | None = None


class PublicHistorialRead(SQLModel):
    estado_desde: str | None
    estado_hacia: str
    created_at: datetime
