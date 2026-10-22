from decimal import Decimal

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.modules.local_config.models import ZonaEnvio
from app.modules.local_config.schemas import (
    ZonaEnvioRead,
    ZonasEnvioListRead,
    ZonasEnvioReplaceRequest,
)


def _norm_ciudad(ciudad: str | None) -> str:
    return (ciudad or "").strip().casefold()


class ZonasEnvioService:
    DEFAULT_COSTO = Decimal("50.00")
    DEFAULT_MINIMO = Decimal("0.00")

    def __init__(self, session: Session):
        self.session = session

    def _activas(self) -> list[ZonaEnvio]:
        return list(
            self.session.exec(
                select(ZonaEnvio)
                .where(ZonaEnvio.activa.is_(True))
                .order_by(ZonaEnvio.orden, ZonaEnvio.id)
            ).all()
        )

    def resolve(self, ciudad: str | None) -> ZonaEnvio | None:
        key = _norm_ciudad(ciudad)
        zonas = self._activas()
        if key:
            for z in zonas:
                if z.ciudad_match and _norm_ciudad(z.ciudad_match) == key:
                    return z
        for z in zonas:
            if not z.ciudad_match or not z.ciudad_match.strip():
                return z
        return None

    def costo_y_minimo(self, ciudad: str | None) -> tuple[Decimal, Decimal, str | None]:
        z = self.resolve(ciudad)
        if not z:
            return self.DEFAULT_COSTO, self.DEFAULT_MINIMO, None
        return (
            Decimal(str(z.costo_envio)).quantize(Decimal("0.01")),
            Decimal(str(z.pedido_minimo)).quantize(Decimal("0.01")),
            z.nombre,
        )

    def assert_subtotal_delivery(self, subtotal: Decimal, ciudad: str | None) -> Decimal:
        costo, minimo, nombre = self.costo_y_minimo(ciudad)
        if subtotal < minimo:
            zona = f" ({nombre})" if nombre else ""
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Pedido mínimo para envío{zona}: ${minimo:.2f}",
            )
        return costo

    def list_public(self) -> list[ZonaEnvioRead]:
        rows = self.session.exec(select(ZonaEnvio).where(ZonaEnvio.activa.is_(True)).order_by(ZonaEnvio.orden)).all()
        return [self._to_read(r) for r in rows]

    def list_admin(self) -> ZonasEnvioListRead:
        rows = self.session.exec(select(ZonaEnvio).order_by(ZonaEnvio.orden, ZonaEnvio.id)).all()
        return ZonasEnvioListRead(zonas=[self._to_read(r) for r in rows])

    def replace_all(self, body: ZonasEnvioReplaceRequest) -> ZonasEnvioListRead:
        defaults = [z for z in body.zonas if not (z.ciudad_match or "").strip()]
        if len(defaults) != 1:
            raise ValueError("Debe existir exactamente una zona default (sin ciudad)")

        for z in body.zonas:
            if z.costo_envio < 0 or z.pedido_minimo < 0:
                raise ValueError("Costos y mínimos no pueden ser negativos")

        keys = [_norm_ciudad(z.ciudad_match) for z in body.zonas if (z.ciudad_match or "").strip()]
        if len(keys) != len(set(keys)):
            raise ValueError("Ciudad duplicada en zonas")

        for row in self.session.exec(select(ZonaEnvio)).all():
            self.session.delete(row)
        self.session.flush()

        for idx, item in enumerate(sorted(body.zonas, key=lambda x: x.orden)):
            ciudad = (item.ciudad_match or "").strip() or None
            self.session.add(
                ZonaEnvio(
                    nombre=item.nombre.strip(),
                    ciudad_match=ciudad,
                    costo_envio=Decimal(str(item.costo_envio)).quantize(Decimal("0.01")),
                    pedido_minimo=Decimal(str(item.pedido_minimo)).quantize(Decimal("0.01")),
                    activa=item.activa,
                    orden=item.orden if item.orden is not None else idx,
                )
            )

        self.session.commit()
        return self.list_admin()

    @staticmethod
    def _to_read(row: ZonaEnvio) -> ZonaEnvioRead:
        return ZonaEnvioRead(
            id=row.id,
            nombre=row.nombre,
            ciudad_match=row.ciudad_match,
            costo_envio=float(row.costo_envio),
            pedido_minimo=float(row.pedido_minimo),
            activa=row.activa,
            orden=row.orden,
        )
