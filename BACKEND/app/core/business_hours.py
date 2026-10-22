"""Apertura/cierre en hora Argentina."""

from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    TZ_AR = ZoneInfo("America/Argentina/Buenos_Aires")
except ZoneInfoNotFoundError:
    # Windows sin paquete tzdata (pip install tzdata)
    TZ_AR = timezone(timedelta(hours=-3))

DIA_NOMBRES = (
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
)


@dataclass(frozen=True)
class DaySchedule:
    weekday: int
    cerrado: bool
    opens_at: time | None
    closes_at: time | None


def _time_in_range(now_t: time, opens: time, closes: time) -> bool:
    """Rango inclusivo en hora local; soporta cierre después de medianoche."""
    if opens == closes:
        return False
    if opens < closes:
        return opens <= now_t < closes
    return now_t >= opens or now_t < closes


def _open_on_day(day: DaySchedule | None, now_t: time) -> bool:
    if day is None:
        return False
    if day.cerrado:
        return False
    if day.opens_at is None or day.closes_at is None:
        return True
    return _time_in_range(now_t, day.opens_at, day.closes_at)


def is_open_at(schedules: list[DaySchedule], moment: datetime | None = None) -> bool:
    if not schedules:
        return True
    now = (moment or datetime.now(TZ_AR)).astimezone(TZ_AR)
    weekday = now.weekday()
    now_t = now.time()
    by_day = {s.weekday: s for s in schedules}

    if _open_on_day(by_day.get(weekday), now_t):
        return True

    prev_weekday = (weekday - 1) % 7
    prev = by_day.get(prev_weekday)
    if (
        prev
        and not prev.cerrado
        and prev.opens_at
        and prev.closes_at
        and prev.opens_at > prev.closes_at
    ):
        return now_t < prev.closes_at
    return False


def format_day_schedule(day: DaySchedule) -> str | None:
    if day.cerrado:
        return "Cerrado"
    if day.opens_at is None or day.closes_at is None:
        return "Abierto todo el día"
    return f"{day.opens_at.strftime('%H:%M')} – {day.closes_at.strftime('%H:%M')}"


def horario_hoy_text(schedules: list[DaySchedule], moment: datetime | None = None) -> str | None:
    if not schedules:
        return None
    now = (moment or datetime.now(TZ_AR)).astimezone(TZ_AR)
    day = next((s for s in schedules if s.weekday == now.weekday()), None)
    if not day:
        return None
    return format_day_schedule(day)


def proxima_apertura_text(schedules: list[DaySchedule], moment: datetime | None = None) -> str | None:
    if not schedules or is_open_at(schedules, moment):
        return None
    now = (moment or datetime.now(TZ_AR)).astimezone(TZ_AR)
    for offset in range(1, 8):
        probe = now + timedelta(days=offset)
        day = next((s for s in schedules if s.weekday == probe.weekday()), None)
        if not day or day.cerrado or not day.opens_at:
            continue
        nombre = DIA_NOMBRES[day.weekday]
        return f"Abrimos {nombre} a las {day.opens_at.strftime('%H:%M')}"
    return None
