from sqlmodel import SQLModel, Field
from sqlalchemy import Column, BigInteger, ForeignKey
from datetime import datetime

class ProductoCategoria(SQLModel, table=True):
    __tablename__ = "producto_categoria"
    producto_id: int = Field(sa_column=Column(BigInteger, ForeignKey("producto.id"), primary_key=True))
    categoria_id: int = Field(sa_column=Column(BigInteger, ForeignKey("categoria.id"), primary_key=True))
    es_principal: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class ProductoIngrediente(SQLModel, table=True):
    __tablename__ = "producto_ingrediente"
    producto_id: int = Field(sa_column=Column(BigInteger, ForeignKey("producto.id"), primary_key=True))
    ingrediente_id: int = Field(sa_column=Column(BigInteger, ForeignKey("ingrediente.id"), primary_key=True))
    es_removible: bool = Field(default=False, nullable=False)
    