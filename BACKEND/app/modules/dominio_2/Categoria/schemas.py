from pydantic import BaseModel, Field
from datetime import datetime


class CategoriaBase(BaseModel):
    parent_id: int | None = Field(None, description="ID de la categoría padre si existe")
    nombre: str = Field(..., min_length=3, max_length=100, examples=["Pizzas"])
    descripcion: str | None = Field(None, max_length=250)
    imagen_url: str | None = Field(None, examples=["https://link.com/imagen.jpg"])


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    parent_id: int | None = None
    nombre: str | None = Field(None, min_length=3, max_length=100)
    descripcion: str | None = None
    imagen_url: str | None = None


class CategoriaRead(CategoriaBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = {"from_attributes": True}


class CategoriaList(BaseModel):
    data: list[CategoriaRead]
    total: int


class ImagenCategoriaUpdate(BaseModel):
    """Actualiza solo la imagen_url de una categoría."""
    imagen_url: str | None = None
