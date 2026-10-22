from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.core.pedido_fsm import ESTADO_EN_CAMINO, ESTADO_ENTREGADO, ESTADO_PREPARADO
from app.core.ws_manager import ws_manager
from app.modules.dominio_1.direcciones.geocode import ensure_direccion_coords
from app.modules.dominio_3.pedidos.models import Pedido
from app.modules.public.schemas import (
    PublicRiderPedidoRead,
    PublicRiderUbicacionInput,
    PublicUbicacionRead,
)


def _get_pedido_by_rider_token(session: Session, rider_token: str) -> Pedido:
    pedido = session.exec(
        select(Pedido).where(Pedido.rider_token == rider_token, Pedido.deleted_at.is_(None))
    ).first()
    if not pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Envío no encontrado")
    if pedido.tipo_pedido != "DELIVERY":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es un pedido de envío")
    return pedido


class EntregaPublicService:
    def __init__(self, session: Session):
        self.session = session

    def rider_pedido(self, rider_token: str) -> PublicRiderPedidoRead:
        pedido = _get_pedido_by_rider_token(self.session, rider_token)
        dest = self._destino(pedido)
        return PublicRiderPedidoRead(
            pedido_id=pedido.id,
            estado_codigo=pedido.estado_codigo,
            destino=dest,
            destino_direccion=self._direccion_texto(pedido),
            puede_reportar=pedido.estado_codigo in (ESTADO_PREPARADO, ESTADO_EN_CAMINO),
        )

    async def actualizar_ubicacion_rider(
        self, rider_token: str, data: PublicRiderUbicacionInput
    ) -> PublicUbicacionRead:
        pedido = _get_pedido_by_rider_token(self.session, rider_token)
        if pedido.estado_codigo not in (ESTADO_PREPARADO, ESTADO_EN_CAMINO):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El pedido no está en reparto",
            )

        pedido.rider_lat = data.lat
        pedido.rider_lng = data.lng
        pedido.rider_location_at = datetime.now(timezone.utc)
        pedido.updated_at = pedido.rider_location_at
        self.session.add(pedido)
        self.session.commit()
        self.session.refresh(pedido)

        payload = {
            "event": "rider_location",
            "pedido_id": pedido.id,
            "timestamp": pedido.rider_location_at.isoformat(),
            "data": {
                "lat": pedido.rider_lat,
                "lng": pedido.rider_lng,
                "rider_updated_at": pedido.rider_location_at.isoformat(),
            },
        }
        await ws_manager.broadcast_order_only(pedido.id, payload)

        return PublicUbicacionRead(lat=pedido.rider_lat, lng=pedido.rider_lng)

    def _destino(self, pedido: Pedido) -> PublicUbicacionRead | None:
        if not pedido.direccion:
            return None
        if pedido.direccion.latitud is None or pedido.direccion.longitud is None:
            ensure_direccion_coords(self.session, pedido.direccion)
        if pedido.direccion.latitud is None or pedido.direccion.longitud is None:
            return None
        return PublicUbicacionRead(lat=pedido.direccion.latitud, lng=pedido.direccion.longitud)

    @staticmethod
    def _direccion_texto(pedido: Pedido) -> str | None:
        if not pedido.direccion:
            return None
        parts = [pedido.direccion.linea1]
        if pedido.direccion.linea2:
            parts.append(pedido.direccion.linea2)
        parts.append(f"{pedido.direccion.ciudad}, {pedido.direccion.provincia}")
        return ", ".join(parts)

    @staticmethod
    def seguimiento_mapa_activo(pedido: Pedido) -> bool:
        if pedido.tipo_pedido != "DELIVERY":
            return False
        if pedido.estado_codigo in (ESTADO_ENTREGADO, "CANCELADO"):
            return False
        return pedido.estado_codigo in (ESTADO_PREPARADO, ESTADO_EN_CAMINO)
