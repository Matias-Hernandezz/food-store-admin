from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import BigInteger, UniqueConstraint

if TYPE_CHECKING:
    from app.modules.dominio_1.direcciones.models import DireccionEntrega
    from app.modules.dominio_1.auth.models import RefreshToken


class UsuarioRol(SQLModel, table=True):
    __tablename__ = "usuario_rol"
    __table_args__ = (UniqueConstraint("usuario_id", "rol_codigo"),)

    usuario_id: int = Field(foreign_key="usuario.id", primary_key=True)
    rol_codigo: str = Field(foreign_key="rol.codigo", primary_key=True, max_length=30)
    expires_at: Optional[datetime] = Field(default=None)


class Rol(SQLModel, table=True):
    __tablename__ = "rol"

    codigo: str = Field(primary_key=True, max_length=30)
    nombre: str = Field(max_length=80)
    descripcion: Optional[str] = Field(default=None, max_length=250)

    usuarios: List["Usuario"] = Relationship(
        back_populates="roles",
        link_model=UsuarioRol,
    )


class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True),
    )
    nombre: str = Field(max_length=80)
    apellido: str = Field(max_length=80)
    email: str = Field(max_length=150, unique=True, index=True)
    celular: Optional[str] = Field(default=None, max_length=30)
    password_hash: str = Field(max_length=128)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(default=None)

    direcciones: List["DireccionEntrega"] = Relationship(back_populates="usuario")
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="usuario")
    roles: List["Rol"] = Relationship(
        back_populates="usuarios",
        link_model=UsuarioRol,
    )
