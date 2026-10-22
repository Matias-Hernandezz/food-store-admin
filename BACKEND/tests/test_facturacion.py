"""Facturación fiscal (mock)."""

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.modules.facturacion.models import ConfigFiscal
from tests.helpers import login_as


def test_emitir_mock(client: TestClient, db_session: Session, admin_user, pedido_factory, client_user):
    cfg = db_session.exec(__import__("sqlmodel").select(ConfigFiscal)).first()
    cfg.habilitado = True
    cfg.adapter = "mock"
    db_session.add(cfg)
    db_session.commit()

    login_as(client, admin_user["email"], admin_user["password"])
    pedido = pedido_factory(usuario_id=client_user["id"])

    res = client.post(f"/api/v1/facturacion/pedidos/{pedido.id}/emitir")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["estado"] == "AUTORIZADO"
    assert body["cae"]
    assert body["qr_payload"]
