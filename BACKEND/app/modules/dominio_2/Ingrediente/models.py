from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from app.modules.dominio_2.Producto.models_shared import ProductoIngrediente 

if TYPE_CHECKING:
    from app.modules.dominio_2.Producto.models import Producto

class Ingrediente(SQLModel, table=True):
    __tablename__ = "ingrediente"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100, unique=True, nullable=False)
    descripcion: Optional[str] = Field(default=None)
    es_alergeno: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    productos: List["Producto"] = Relationship(
        back_populates="ingredientes", 
        link_model=ProductoIngrediente  
    )