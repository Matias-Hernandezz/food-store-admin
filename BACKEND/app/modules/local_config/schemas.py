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


class LocalPerfilRead(SQLModel):
    nombre_negocio: str
    telefono: str | None = None
    email_contacto: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    whatsapp: str | None = None


class LocalPerfilUpdate(SQLModel):
    nombre_negocio: str | None = Field(default=None, min_length=1, max_length=120)
    telefono: str | None = Field(default=None, max_length=40)
    email_contacto: str | None = Field(default=None, max_length=150)
    direccion: str | None = Field(default=None, max_length=250)
    ciudad: str | None = Field(default=None, max_length=100)
    whatsapp: str | None = Field(default=None, max_length=40)


class DeliveryFeeRead(SQLModel):
    delivery_app_fee_percent: float
    usa_default_global: bool
    tenant_slug: str | None = None


class DeliveryFeeUpdate(SQLModel):
    delivery_app_fee_percent: float = Field(ge=0, le=100)


class ZonaEnvioRead(SQLModel):
    id: int | None = None
    nombre: str
    ciudad_match: str | None = None
    costo_envio: float
    pedido_minimo: float
    activa: bool
    orden: int


class ZonaEnvioWrite(SQLModel):
    id: int | None = None
    nombre: str = Field(min_length=1, max_length=80)
    ciudad_match: str | None = Field(default=None, max_length=120)
    costo_envio: float = Field(ge=0)
    pedido_minimo: float = Field(ge=0)
    activa: bool = True
    orden: int = 0


class ZonasEnvioListRead(SQLModel):
    zonas: list[ZonaEnvioRead]


class ZonasEnvioReplaceRequest(SQLModel):
    zonas: list[ZonaEnvioWrite]

    @field_validator("zonas")
    @classmethod
    def at_least_one(cls, v: list[ZonaEnvioWrite]):
        if not v:
            raise ValueError("Debe haber al menos una zona")
        return v


class PublicCotizarEnvioInput(SQLModel):
    subtotal: float = Field(ge=0)
    ciudad: str | None = None


class PublicCotizarEnvioRead(SQLModel):
    costo_envio: float
    pedido_minimo: float
    alcanza_minimo: bool
    zona_nombre: str | None = None


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
