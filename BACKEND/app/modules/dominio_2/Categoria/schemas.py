from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime

class CategoriaBase(BaseModel):
    parent_id: Optional[int] = Field(None, description="ID de la categoría padre si existe")
    nombre: str = Field(..., min_length=3, max_length=100, examples=["Pizzas"])
    descripcion: Optional[str] = Field(None, max_length=250)
    imagen_url: Optional[str] = Field(None, examples=["https://link.com/imagen.jpg"])

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    parent_id: Optional[int] = None
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None

class CategoriaRead(CategoriaBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CategoriaList(BaseModel):
    data: List[CategoriaRead]
    total: int 