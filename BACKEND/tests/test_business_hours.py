from datetime import datetime, time
from zoneinfo import ZoneInfo

from app.core.business_hours import DaySchedule, is_open_at

TZ = ZoneInfo("America/Argentina/Buenos_Aires")


def _sched():
    return [
        DaySchedule(weekday=i, cerrado=False, opens_at=time(20, 0), closes_at=time(23, 59))
        for i in range(7)
    ]


def test_abierto_dentro_de_franja():
    moment = datetime(2026, 6, 21, 21, 0, tzinfo=TZ)  # domingo 21:00
    assert is_open_at(_sched(), moment) is True


def test_cerrado_fuera_de_franja():
    moment = datetime(2026, 6, 21, 15, 0, tzinfo=TZ)
    assert is_open_at(_sched(), moment) is False


def test_sin_horarios_configurados_abierto():
    moment = datetime(2026, 6, 21, 3, 0, tzinfo=TZ)
    assert is_open_at([], moment) is True


def test_cierre_post_medianoche():
    sched = [DaySchedule(weekday=0, cerrado=False, opens_at=time(20, 0), closes_at=time(2, 0))]
    lunes_noche = datetime(2026, 6, 22, 23, 30, tzinfo=TZ)  # lunes
    assert is_open_at(sched, lunes_noche) is True
    martes_madrugada = datetime(2026, 6, 23, 1, 0, tzinfo=TZ)
    assert is_open_at(sched, martes_madrugada) is True
    martes_tarde = datetime(2026, 6, 23, 10, 0, tzinfo=TZ)
    assert is_open_at(sched, martes_tarde) is False
