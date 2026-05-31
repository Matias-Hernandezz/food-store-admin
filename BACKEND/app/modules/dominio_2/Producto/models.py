from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal
from sqlalchemy import Column, BigInteger, CheckConstraint, text, ForeignKey

# 1. IMPORTACIONES REALES
# Importamos las tablas de unión desde el archivo compartido para romper el círculo
from app.modules.dominio_2.Producto.models_shared import ProductoCategoria, ProductoIngrediente

# 2. IMPORTACIONES DE TIPADO
from app.modules.dominio_2.Categoria.models import Categoria
from app.modules.dominio_2.Ingrediente.models import Ingrediente

class Producto(SQLModel, table=True):
    __tablename__ = "producto"


    __table_args__ = (
        CheckConstraint("precio_base >= 0", name="check_precio_positivo"),
        CheckConstraint("stock_cantidad >= 0", name="check_stock_positivo"),
    )


    id: Optional[int] = Field(
        default=None, 
        sa_column=Column(BigInteger, primary_key=True)
    )
    nombre: str = Field(index=True, max_length=150, nullable=False, unique=True)
    descripcion: Optional[str] = Field(default=None)
    
    precio_base: Decimal = Field(
        default=0, 
        max_digits=10, 
        decimal_places=2,
        nullable=False
    )
    
    imagenes_url: Optional[str] = Field(default=None)
    stock_cantidad: int = Field(default=0, nullable=False)
    disponible: bool = Field(default=True, nullable=False)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": text("CURRENT_TIMESTAMP")},
        nullable=False
    )
    deleted_at: Optional[datetime] = Field(default=None)

    categorias: List["Categoria"] = Relationship(
        back_populates="productos", 
        link_model=ProductoCategoria
    )
    
    ingredientes: List["Ingrediente"] = Relationship(
        back_populates="productos",
        link_model=ProductoIngrediente
    )