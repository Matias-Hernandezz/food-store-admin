from datetime import datetime
from pydantic import BaseModel, Field


class LoginInput(BaseModel):
    email: str = Field(..., max_length=150)
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    """Respuesta con tokens (rúbrica §6.1)."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: str
    celular: str | None = None
    roles: list[str] = []
    created_at: datetime
    deleted_at: datetime | None = None
    token_type: str = "bearer"
    expires_in: int

    model_config = {"from_attributes": True}


class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=80)
    apellido: str = Field(..., min_length=2, max_length=80)
    email: str = Field(..., max_length=150)
    celular: str | None = Field(None, max_length=30)
    password: str = Field(..., min_length=6)
