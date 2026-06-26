from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import CheckConstraint, Column, DateTime, Index, text

from app.modules.dominio_2.productos.models_shared import ProductoIngrediente

if TYPE_CHECKING:
    from app.modules.dominio_2.productos.models import Producto


class Ingrediente(SQLModel, table=True):
    __tablename__ = "ingrediente"

    __table_args__ = (
        CheckConstraint("stock_cantidad >= 0", name="check_ingrediente_stock_positivo"),
        Index("ix_ingrediente_nombre_active", "nombre", unique=True,
              postgresql_where=text("deleted_at IS NULL")),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100, nullable=False)
    descripcion: Optional[str] = Field(default=None)
    es_alergeno: bool = Field(default=False)
    stock_cantidad: int = Field(default=0, nullable=False)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, onupdate=lambda: datetime.now(timezone.utc)),
    )
    deleted_at: Optional[datetime] = Field(default=None)

    productos: List["Producto"] = Relationship(
        back_populates="ingredientes",
        link_model=ProductoIngrediente,
    )
