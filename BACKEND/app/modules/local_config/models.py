from datetime import time

from sqlmodel import Field, SQLModel


class HorarioLocal(SQLModel, table=True):
    """Una fila por día de la semana (0=Lunes … 6=Domingo) en la DB del local."""

    __tablename__ = "horario_local"

    weekday: int = Field(primary_key=True, ge=0, le=6)
    cerrado: bool = Field(default=False)
    opens_at: time | None = Field(default=None)
    closes_at: time | None = Field(default=None)
