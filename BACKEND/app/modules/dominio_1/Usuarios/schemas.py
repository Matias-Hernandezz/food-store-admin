from datetime import datetime
from pydantic import BaseModel, Field


class UsuarioRead(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: str
    celular: str | None = None
    roles: list[str] = []
    created_at: datetime
    deleted_at: datetime | None = None

    model_config = {"from_attributes": True}


class UsuarioUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=2, max_length=80)
    apellido: str | None = Field(None, min_length=2, max_length=80)
    celular: str | None = Field(None, max_length=30)
