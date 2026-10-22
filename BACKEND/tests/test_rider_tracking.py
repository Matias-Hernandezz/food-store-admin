"""Tracking de repartidor (envío)."""

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.pedido_fsm import ESTADO_EN_PREPARACION, ESTADO_PREPARADO
from app.modules.dominio_3.pedidos.models import Pedido, new_rider_token
from tests.helpers import login_as


def test_rider_ubicacion_y_seguimiento_publico(
    client: TestClient,
    db_session: Session,
    admin_user,
    client_user,
    pedido_factory,
):
    pedido = pedido_factory(usuario_id=client_user["id"], estado=ESTADO_PREPARADO)
    p = db_session.get(Pedido, pedido.id)
    p.tipo_pedido = "DELIVERY"
    p.rider_token = new_rider_token()
    p.tracking_token = p.tracking_token or "track-test-token-123456789012345678901234"
    db_session.add(p)
    db_session.commit()

    res = client.post(
        f"/api/v1/public/envio/rider/{p.rider_token}/ubicacion",
        json={"lat": -34.6, "lng": -58.38},
    )
    assert res.status_code == 200, res.text

    seg = client.get(f"/api/v1/public/pedidos/seguimiento/{p.tracking_token}")
    assert seg.status_code == 200
    body = seg.json()
    assert body["seguimiento_mapa_activo"] is True
    assert body["rider"]["lat"] == -34.6


def test_rider_token_generado_al_preparado_delivery(
    client: TestClient,
    db_session: Session,
    admin_user,
    client_user,
    pedido_factory,
):
    login_as(client, admin_user["email"], admin_user["password"])
    pedido = pedido_factory(usuario_id=client_user["id"], estado=ESTADO_EN_PREPARACION)
    p = db_session.get(Pedido, pedido.id)
    p.tipo_pedido = "DELIVERY"
    db_session.add(p)
    db_session.commit()

    res = client.patch(
        f"/api/v1/pedidos/{p.id}/estado",
        json={"nuevo_estado": ESTADO_PREPARADO},
    )
    assert res.status_code == 200, res.text
    assert res.json().get("rider_token")
