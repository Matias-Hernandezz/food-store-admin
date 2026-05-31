from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, BigInteger, text, ForeignKey

from app.modules.dominio_2.Producto.models_shared import ProductoCategoria

if TYPE_CHECKING:
    from app.modules.dominio_2.Producto.models import Producto

class Categoria(SQLModel, table=True):
    __tablename__ = "categoria"

    id: Optional[int] = Field(
        default=None, 
        sa_column=Column(BigInteger, primary_key=True)
    )
    
    parent_id: Optional[int] = Field(
        default=None, 
        sa_column=Column(BigInteger, ForeignKey("categoria.id"), nullable=True)
    )
    
    nombre: str = Field(index=True, max_length=100, nullable=False, unique=True)
    descripcion: Optional[str] = Field(default=None, max_length=250)
    imagen_url: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": text("CURRENT_TIMESTAMP")},
        nullable=False
    )
    deleted_at: Optional[datetime] = Field(default=None)



    productos: List["Producto"] = Relationship(
        back_populates="categorias", 
        link_model=ProductoCategoria
    )

    subcategorias: List["Categoria"] = Relationship(
        back_populates="padre"
    )
    
    padre: Optional["Categoria"] = Relationship(
        sa_relationship_kwargs={"remote_side": "Categoria.id"},
        back_populates="subcategorias"
    )