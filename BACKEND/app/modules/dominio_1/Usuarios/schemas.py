from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
class RolRead(SQLModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    
class AsignarRolInput(SQLModel):
    roles: List[str]
    
class UsuarioCreate(SQLModel):
    nombre:   str = Field(min_length=2, max_length=80)
    apellido: str = Field(min_length=2, max_length=80)
    email:    EmailStr
    celular:  Optional[str] = Field(default=None, max_length=20)
    password: str = Field(min_length=8)
 
 
class UsuarioRead(SQLModel):
    id:        int
    nombre:    str
    apellido:  str
    email:     str
    celular:   Optional[str]
    roles:     List[str] = []   
    created_at: datetime
    deleted_at: Optional[datetime]
 
 
class UsuarioUpdate(SQLModel):
    nombre:   Optional[str] = Field(default=None, max_length=80)
    apellido: Optional[str] = Field(default=None, max_length=80)
    celular:  Optional[str] = Field(default=None, max_length=20)
 
 
class Token(SQLModel):
    token_type: str = "bearer"
    expires_in: int              
 
 
class LoginResponse(UsuarioRead):
    """Respuesta combinada: datos del usuario + tokens de acceso."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginInput(SQLModel):
    email:    EmailStr
    password: str

class DireccionCreate(SQLModel):
    alias:         Optional[str] = Field(default=None, max_length=50)
    linea1:        str
    linea2:        Optional[str] = None
    ciudad:        str = Field(min_length=1, max_length=100)
    provincia:     Optional[str] = Field(default=None, max_length=100)
    codigo_postal: Optional[str] = Field(default=None, max_length=10)
    latitud:       Optional[Decimal] = None
    longitud:      Optional[Decimal] = None
    es_principal:  bool = False
    
class DireccionUpdate(SQLModel):
    alias: Optional[str] = Field(default=None, max_length=50)
    linea1: Optional[str] = None
    linea2: Optional[str] = None
    ciudad: Optional[str] = Field(default=None, max_length=100)
    provincia: Optional[str] = Field(default=None, max_length=100)
    codigo_postal: Optional[str] = Field(default=None, max_length=10)
    es_principal: Optional[bool] = None
 
class DireccionRead(SQLModel):
    id:            int
    usuario_id:    int
    alias:         Optional[str] = None
    linea1:        str
    linea2:        Optional[str] = None
    ciudad:        str
    provincia:     Optional[str] = None
    codigo_postal: Optional[str] = None
    es_principal:  bool
    deleted_at:    Optional[datetime] = None

 
