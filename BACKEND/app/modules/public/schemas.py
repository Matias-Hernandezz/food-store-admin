from datetime import datetime
from decimal import Decimal

from pydantic import EmailStr, Field
from sqlmodel import SQLModel

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


class PublicZonaEnvioRead(SQLModel):
    nombre: str
    ciudad_match: str | None = None
    costo_envio: Decimal
    pedido_minimo: Decimal


class PublicTiendaRead(SQLModel):
    abierto: bool
    mensaje: str | None = None
    horario_hoy: str | None = None
    proxima_apertura: str | None = None
    zonas_envio: list[PublicZonaEnvioRead] = []


class PublicClienteInput(SQLModel):
    nombre: str = Field(min_length=1, max_length=80)
    apellido: str = Field(min_length=1, max_length=80)
    email: EmailStr
    celular: str | None = Field(default=None, max_length=30)


class PublicDireccionCreate(SQLModel):
    """Checkout invitado: provincia y CP opcionales (el formulario no siempre los pide)."""

    alias: str = Field(default="Entrega", max_length=80)
    linea1: str = Field(min_length=1, max_length=200)
    linea2: str | None = Field(default=None, max_length=200)
    ciudad: str = Field(min_length=1, max_length=100)
    provincia: str = Field(default="", max_length=100)
    codigo_postal: str = Field(default="", max_length=20)
    latitud: float | None = None
    longitud: float | None = None


class PublicPedidoCreate(SQLModel):
    cliente: PublicClienteInput
    items: list[ItemCarritoInput]
    forma_pago_codigo: str
    tipo_pedido: str | None = None
    direccion_id: int | None = None
    direccion: PublicDireccionCreate | None = None
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


class PublicUbicacionRead(SQLModel):
    lat: float
    lng: float


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
    destino: PublicUbicacionRead | None = None
    destino_direccion: str | None = None
    rider: PublicUbicacionRead | None = None
    rider_updated_at: datetime | None = None
    seguimiento_mapa_activo: bool = False


class PublicRiderUbicacionInput(SQLModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class PublicRiderPedidoRead(SQLModel):
    pedido_id: int
    estado_codigo: str
    destino: PublicUbicacionRead | None
    destino_direccion: str | None
    puede_reportar: bool


class PublicHistorialRead(SQLModel):
    estado_desde: str | None
    estado_hacia: str
    created_at: datetime
