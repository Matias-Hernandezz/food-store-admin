from datetime import time

from pydantic import Field, field_validator
from sqlmodel import SQLModel

from app.core.business_hours import DIA_NOMBRES


class HorarioDiaRead(SQLModel):
    weekday: int
    dia_nombre: str
    cerrado: bool
    opens_at: time | None
    closes_at: time | None
    etiqueta: str | None = None


class HorarioDiaUpdate(SQLModel):
    weekday: int = Field(ge=0, le=6)
    cerrado: bool = False
    opens_at: time | None = None
    closes_at: time | None = None

    @field_validator("opens_at", "closes_at", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


class HorariosEstadoRead(SQLModel):
    abierto: bool
    mensaje: str | None = None
    horario_hoy: str | None = None
    proxima_apertura: str | None = None
    dias: list[HorarioDiaRead]


class HorariosUpdateRequest(SQLModel):
    dias: list[HorarioDiaUpdate]

    @field_validator("dias")
    @classmethod
    def seven_unique_days(cls, v: list[HorarioDiaUpdate]):
        if len(v) != 7:
            raise ValueError("Deben enviarse exactamente 7 días (0–6)")
        weekdays = [d.weekday for d in v]
        if len(set(weekdays)) != 7:
            raise ValueError("weekday duplicado")
        return v


def to_horario_read(weekday: int, cerrado: bool, opens_at, closes_at) -> HorarioDiaRead:
    from app.core.business_hours import DaySchedule, format_day_schedule

    etiqueta = format_day_schedule(
        DaySchedule(weekday=weekday, cerrado=cerrado, opens_at=opens_at, closes_at=closes_at)
    )
    return HorarioDiaRead(
        weekday=weekday,
        dia_nombre=DIA_NOMBRES[weekday],
        cerrado=cerrado,
        opens_at=opens_at,
        closes_at=closes_at,
        etiqueta=etiqueta,
    )
