from datetime import datetime
from pydantic import BaseModel, Field


class DireccionCreate(BaseModel):
    alias: str = Field(..., max_length=80)
    linea1: str = Field(..., max_length=200)
    linea2: str | None = Field(None, max_length=200)
    ciudad: str = Field(..., max_length=100)
    provincia: str = Field(..., max_length=100)
    codigo_postal: str = Field(..., max_length=20)
    latitud: float | None = None
    longitud: float | None = None


class DireccionUpdate(BaseModel):
    alias: str | None = Field(None, max_length=80)
    linea1: str | None = Field(None, max_length=200)
    linea2: str | None = Field(None, max_length=200)
    ciudad: str | None = Field(None, max_length=100)
    provincia: str | None = Field(None, max_length=100)
    codigo_postal: str | None = Field(None, max_length=20)
    latitud: float | None = None
    longitud: float | None = None


class DireccionRead(BaseModel):
    id: int
    alias: str
    linea1: str
    linea2: str | None = None
    ciudad: str
    provincia: str
    codigo_postal: str | None = None
    latitud: float | None = None
    longitud: float | None = None
    es_principal: bool = False
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = {"from_attributes": True}
