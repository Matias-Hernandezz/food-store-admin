from datetime import time
from decimal import Decimal

from sqlalchemy import Column, Numeric
from sqlmodel import Field, SQLModel


class HorarioLocal(SQLModel, table=True):
    """Una fila por día de la semana (0=Lunes … 6=Domingo) en la DB del local."""

    __tablename__ = "horario_local"

    weekday: int = Field(primary_key=True, ge=0, le=6)
    cerrado: bool = Field(default=False)
    opens_at: time | None = Field(default=None)
    closes_at: time | None = Field(default=None)


class LocalPerfil(SQLModel, table=True):
    """Datos públicos del local (fila única id=1)."""

    __tablename__ = "local_perfil"

    id: int = Field(primary_key=True, default=1)
    nombre_negocio: str = Field(default="Food Store", max_length=120)
    telefono: str | None = Field(default=None, max_length=40)
    email_contacto: str | None = Field(default=None, max_length=150)
    direccion: str | None = Field(default=None, max_length=250)
    ciudad: str | None = Field(default=None, max_length=100)
    whatsapp: str | None = Field(default=None, max_length=40)


class ZonaEnvio(SQLModel, table=True):
    """Zona de envío por ciudad (ciudad_match) o fila default (ciudad_match NULL)."""

    __tablename__ = "zona_envio"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=80)
    ciudad_match: str | None = Field(default=None, max_length=120, index=True)
    costo_envio: Decimal = Field(
        default=Decimal("50.00"),
        sa_column=Column(Numeric(10, 2), nullable=False),
    )
    pedido_minimo: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(10, 2), nullable=False),
    )
    activa: bool = Field(default=True)
    orden: int = Field(default=0)
