from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Numeric, Text
from sqlmodel import Field, SQLModel


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class TurnoCaja(SQLModel, table=True):
    __tablename__ = "turno_caja"

    id: Optional[int] = Field(default=None, primary_key=True)
    estado: str = Field(default="OPEN", max_length=20, index=True)
    abierto_en: datetime = Field(default_factory=now_utc)
    cerrado_en: datetime | None = Field(default=None)
    usuario_apertura_id: int = Field(foreign_key="usuario.id")
    usuario_cierre_id: int | None = Field(default=None, foreign_key="usuario.id")
    fondo_inicial: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(12, 2), nullable=False),
    )
    efectivo_esperado: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(12, 2), nullable=True),
    )
    efectivo_contado: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(12, 2), nullable=True),
    )
    notas_cierre: str | None = Field(default=None, sa_column=Column(Text))
