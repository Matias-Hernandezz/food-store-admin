from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=150, examples=["Hamburguesa Doble Queso"])
    descripcion: Optional[str] = Field(None, examples=["Hamburguesa con cheddar y bacon(explotada en rica)"])
    precio_base: Decimal = Field(..., ge=0, examples=[1500.50]) 
    imagenes_url: Optional[str] = Field(default=None, examples=["https://link.com/foto1.jpg"])
    stock_cantidad: int = Field(default=0, ge=0)
    disponible: bool = Field(default=True)

class ProductoCreate(ProductoBase):
    categoria_ids: List[int] = Field(default=[], description="Lista de IDs de categorias")
    ingrediente_ids: Optional[List[int]] = Field(default=[], description="Lista de IDs de ingredientes")

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=150)
    descripcion: Optional[str] = None
    precio_base: Optional[Decimal] = Field(None, ge=0)
    imagenes_url: Optional[str] = None
    stock_cantidad: Optional[int] = Field(None, ge=0)
    disponible: Optional[bool] = None
    categoria_ids: Optional[List[int]] = Field(None, description="Lista de IDs de categorias")
    ingrediente_ids: Optional[List[int]] = Field(None, description="Lista de IDs de ingredientes")

class ProductoRead(ProductoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    categoria_ids: List[int] = []
    ingrediente_ids: List[int] = []

    class Config:
        from_attributes = True

class ProductoList(BaseModel):
    data: List[ProductoRead]
    total: int

    