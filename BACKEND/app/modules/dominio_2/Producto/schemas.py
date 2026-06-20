from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

from app.modules.dominio_2.unidad_medida.schemas import UnidadMedidaRead


class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=150, examples=["Hamburguesa Doble Queso"])
    descripcion: str | None = Field(None, examples=["Hamburguesa con cheddar y bacon"])
    precio_base: Decimal = Field(..., ge=0, examples=[1500.50])
    imagenes_url: list[str] = Field(default=[], examples=[["https://link.com/foto1.jpg"]])
    stock_cantidad: int = Field(default=0, ge=0)
    disponible: bool = Field(default=True)
    unidad_venta_id: int | None = Field(None)


class ProductoCreate(ProductoBase):
    categoria_ids: list[int] = Field(default=[], description="Lista de IDs de categorias")
    ingrediente_ids: list[int] | None = Field(default=[], description="Lista de IDs de ingredientes")


class ProductoUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=3, max_length=150)
    descripcion: str | None = None
    precio_base: Decimal | None = Field(None, ge=0)
    imagenes_url: list[str] | None = None
    stock_cantidad: int | None = Field(None, ge=0)
    disponible: bool | None = None
    unidad_venta_id: int | None = Field(None)
    categoria_ids: list[int] | None = Field(None, description="Lista de IDs de categorias")
    ingrediente_ids: list[int] | None = Field(None, description="Lista de IDs de ingredientes")


# ── Schemas específicos para endpoints nuevos ────────────────────────────

class DisponibilidadUpdate(BaseModel):
    """Toggle disponible (true/false)."""
    disponible: bool


class ImagenesProductoUpdate(BaseModel):
    """Reemplaza la lista completa de imagenes_url."""
    imagenes_url: list[str]


class ProductoIngredienteCreate(BaseModel):
    """Asocia un ingrediente a un producto con cantidad y unidad."""
    ingrediente_id: int
    cantidad: Decimal = Field(..., gt=0, max_digits=10, decimal_places=3)
    unidad_medida_id: int
    es_removible: bool = False


class ProductoIngredienteRead(BaseModel):
    """Detalle de un ingrediente asociado a un producto."""
    ingrediente_id: int
    nombre: str
    cantidad: Decimal
    unidad_simbolo: str
    es_removible: bool
    es_alergeno: bool

    model_config = {"from_attributes": True}


# ── Read / List ───────────────────────────────────────────────────────────

class ProductoRead(ProductoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    categoria_ids: list[int] = []
    ingrediente_ids: list[int] = []
    unidad_venta: UnidadMedidaRead | None = None

    model_config = {"from_attributes": True}


class ProductoList(BaseModel):
    data: list[ProductoRead]
    total: int
    page: int = 1
    size: int = 20
    pages: int = 1
