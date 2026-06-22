from pydantic import BaseModel, Field
from datetime import datetime


class IngredienteBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, examples=["Cebolla Caramelizada"])
    descripcion: str | None = Field(None, examples=["Cebollas cocidas a fuego lento con azúcar"])
    es_alergeno: bool = Field(default=False)


class IngredienteCreate(IngredienteBase):
    pass


class IngredienteUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=2, max_length=100)
    descripcion: str | None = None
    es_alergeno: bool | None = None


class IngredienteRead(IngredienteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = {"from_attributes": True}


class IngredienteList(BaseModel):
    data: list[IngredienteRead]
    total: int
