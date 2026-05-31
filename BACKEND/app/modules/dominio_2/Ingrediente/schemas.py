from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class IngredienteBase(BaseModel):
  
    nombre: str = Field(..., min_length=2, max_length=100, examples=["Cebolla Caramelizada"])
    descripcion: Optional[str] = Field(None, examples=["Cebollas cocidas a fuego lento con azúcar"])
    es_alergeno: bool = Field(default=False)

class IngredienteCreate(IngredienteBase):
    pass

class IngredienteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = None
    es_alergeno: Optional[bool] = None

class IngredienteRead(IngredienteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IngredienteList(BaseModel):
    data: List[IngredienteRead]
    total: int