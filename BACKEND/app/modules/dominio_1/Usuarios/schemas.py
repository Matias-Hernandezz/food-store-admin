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
    deleted_at: Optional[datetime]
 
 
class UsuarioUpdate(SQLModel):
    nombre:   Optional[str] = Field(default=None, max_length=80)
    apellido: Optional[str] = Field(default=None, max_length=80)
    celular:  Optional[str] = Field(default=None, max_length=20)
 
 
class Token(SQLModel):
    token_type: str = "bearer"
    expires_in: int              
 
 
class LoginInput(SQLModel):
    email:    EmailStr
    password: str

class DireccionCreate(SQLModel):
    alias:         str = Field(min_length=1, max_length=50)
    linea1:        str
    linea2:        Optional[str] = None
    ciudad:        str = Field(min_length=1, max_length=100)
    provincia:     str
    codigo_postal: str = Field(max_length=10)
    latitud:       Optional[Decimal] = None
    longitud:      Optional[Decimal] = None
 
 
class DireccionUpdate(SQLModel):
    alias:         Optional[str] = None
    linea1:        Optional[str] = None
    linea2:        Optional[str] = None
    ciudad:        Optional[str] = None
    provincia:     Optional[str] = None
    codigo_postal: Optional[str] = None
 
 
class DireccionRead(SQLModel):
    id:            int
    usuario_id:    int
    alias:         str
    linea1:        str
    linea2:        Optional[str]
    ciudad:        str
    provincia:     str
    codigo_postal: str
    es_principal:  bool
    deleted_at:    Optional[datetime]

 
