from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from datetime import datetime
from decimal import Decimal


class RolRead(SQLModel):
    codigo: str
    nombre: str
    descripcion: str | None = None


class AsignarRolInput(SQLModel):
    roles: list[str]


class UsuarioCreate(SQLModel):
    nombre:   str = Field(min_length=2, max_length=80)
    apellido: str = Field(min_length=2, max_length=80)
    email:    EmailStr
    celular:  str | None = Field(default=None, max_length=20)
    password: str = Field(min_length=8)


class UsuarioRead(SQLModel):
    id:        int
    nombre:    str
    apellido:  str
    email:     str
    celular:   str | None
    roles:     list[str] = []
    created_at: datetime
    deleted_at: datetime | None


class UsuarioUpdate(SQLModel):
    nombre:   str | None = Field(default=None, max_length=80)
    apellido: str | None = Field(default=None, max_length=80)
    celular:  str | None = Field(default=None, max_length=20)


class Token(SQLModel):
    token_type: str = "bearer"
    expires_in: int


class LoginResponse(UsuarioRead):
    """Respuesta combinada: datos del usuario. Los tokens van solo en cookies httpOnly."""
    token_type: str = "bearer"
    expires_in: int


class LoginInput(SQLModel):
    email:    EmailStr
    password: str


class DireccionCreate(SQLModel):
    alias:         str | None = Field(default=None, max_length=50)
    linea1:        str
    linea2:        str | None = None
    ciudad:        str = Field(min_length=1, max_length=100)
    provincia:     str | None = Field(default=None, max_length=100)
    codigo_postal: str | None = Field(default=None, max_length=10)
    latitud:       Decimal | None = None
    longitud:      Decimal | None = None
    es_principal:  bool = False


class DireccionUpdate(SQLModel):
    alias:         str | None = Field(default=None, max_length=50)
    linea1:        str | None = None
    linea2:        str | None = None
    ciudad:        str | None = Field(default=None, max_length=100)
    provincia:     str | None = Field(default=None, max_length=100)
    codigo_postal: str | None = Field(default=None, max_length=10)
    es_principal:  bool | None = None


class DireccionRead(SQLModel):
    id:            int
    usuario_id:    int
    alias:         str | None = None
    linea1:        str
    linea2:        str | None = None
    ciudad:        str
    provincia:     str | None = None
    codigo_postal: str | None = None
    es_principal:  bool
    deleted_at:    datetime | None = None
