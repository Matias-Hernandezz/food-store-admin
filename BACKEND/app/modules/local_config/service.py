from sqlmodel import Session, select

from app.core.business_hours import (
    DaySchedule,
    horario_hoy_text,
    is_open_at,
    proxima_apertura_text,
)
from app.core.config import settings
from app.modules.local_config.models import HorarioLocal
from app.modules.local_config.schemas import (
    HorarioDiaUpdate,
    HorariosEstadoRead,
    HorariosUpdateRequest,
    to_horario_read,
)


class HorariosService:
    def __init__(self, session: Session):
        self.session = session

    def _load_schedules(self) -> list[DaySchedule]:
        rows = self.session.exec(select(HorarioLocal).order_by(HorarioLocal.weekday)).all()
        return [
            DaySchedule(
                weekday=r.weekday,
                cerrado=r.cerrado,
                opens_at=r.opens_at,
                closes_at=r.closes_at,
            )
            for r in rows
        ]

    def estado_publico(self) -> tuple[bool, str | None, str | None, str | None]:
        schedules = self._load_schedules()
        if not settings.public_tienda_abierta:
            return False, "El local no acepta pedidos temporalmente.", None, None

        abierto = is_open_at(schedules)
        hoy = horario_hoy_text(schedules)
        prox = proxima_apertura_text(schedules) if not abierto else None
        if abierto:
            return True, None, hoy, None
        msg = "Estamos cerrados."
        if prox:
            msg = f"{msg} {prox}."
        elif hoy:
            msg = f"{msg} Hoy: {hoy}."
        return False, msg, hoy, prox

    def puede_aceptar_pedidos(self) -> bool:
        abierto, _, _, _ = self.estado_publico()
        return abierto

    def get_admin(self) -> HorariosEstadoRead:
        schedules = self._load_schedules()
        abierto, mensaje, hoy, prox = self.estado_publico()
        by_day = {r.weekday: r for r in self.session.exec(select(HorarioLocal)).all()}
        dias = []
        for w in range(7):
            row = by_day.get(w)
            if row:
                dias.append(to_horario_read(row.weekday, row.cerrado, row.opens_at, row.closes_at))
            else:
                dias.append(to_horario_read(w, False, None, None))
        return HorariosEstadoRead(
            abierto=abierto,
            mensaje=mensaje,
            horario_hoy=hoy,
            proxima_apertura=prox,
            dias=dias,
        )

    def replace_all(self, body: HorariosUpdateRequest) -> HorariosEstadoRead:
        for item in sorted(body.dias, key=lambda d: d.weekday):
            self._validate_day(item)
            row = self.session.get(HorarioLocal, item.weekday)
            if not row:
                row = HorarioLocal(weekday=item.weekday)
            row.cerrado = item.cerrado
            row.opens_at = item.opens_at
            row.closes_at = item.closes_at
            self.session.add(row)
        self.session.commit()
        return self.get_admin()

    @staticmethod
    def _validate_day(item: HorarioDiaUpdate) -> None:
        if item.cerrado:
            return
        if item.opens_at is None and item.closes_at is None:
            return
        if item.opens_at is None or item.closes_at is None:
            raise ValueError(
                f"Día {item.weekday}: indicá apertura y cierre, o marcá cerrado"
            )
