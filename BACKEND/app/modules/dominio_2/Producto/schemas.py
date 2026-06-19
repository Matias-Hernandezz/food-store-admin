from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from app.modules.dominio_2.unidad_medida.schemas import UnidadMedidaRead


class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=150, examples=["Hamburguesa Doble Queso"])
    descripcion: Optional[str] = Field(None, examples=["Hamburguesa con cheddar y bacon"])
    precio_base: Decimal = Field(..., ge=0, examples=[1500.50])
    imagenes_url: List[str] = Field(default=[], examples=[["https://link.com/foto1.jpg"]])
    stock_cantidad: int = Field(default=0, ge=0)
    disponible: bool = Field(default=True)
    unidad_venta_id: Optional[int] = Field(None)


class ProductoCreate(ProductoBase):
    categoria_ids: List[int] = Field(default=[], description="Lista de IDs de categorias")
    ingrediente_ids: Optional[List[int]] = Field(default=[], description="Lista de IDs de ingredientes")


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=150)
    descripcion: Optional[str] = None
    precio_base: Optional[Decimal] = Field(None, ge=0)
    imagenes_url: Optional[List[str]] = None
    stock_cantidad: Optional[int] = Field(None, ge=0)
    disponible: Optional[bool] = None
    unidad_venta_id: Optional[int] = Field(None)
    categoria_ids: Optional[List[int]] = Field(None, description="Lista de IDs de categorias")
    ingrediente_ids: Optional[List[int]] = Field(None, description="Lista de IDs de ingredientes")


# ── Schemas específicos para endpoints nuevos ────────────────────────────

class DisponibilidadUpdate(BaseModel):
    """Toggle disponible (true/false)."""
    disponible: bool


class ImagenesProductoUpdate(BaseModel):
    """Reemplaza la lista completa de imagenes_url."""
    imagenes_url: List[str]


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

    class Config:
        from_attributes = True


# ── Read / List ───────────────────────────────────────────────────────────

class ProductoRead(ProductoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    categoria_ids: List[int] = []
    ingrediente_ids: List[int] = []
    unidad_venta: Optional[UnidadMedidaRead] = None

    class Config:
        from_attributes = True


class ProductoList(BaseModel):
    data: List[ProductoRead]
    total: int
    page: int = 1
    size: int = 20
    pages: int = 1
