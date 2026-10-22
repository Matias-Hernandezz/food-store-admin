from datetime import time

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.modules.local_config.models import HorarioLocal
from tests.helpers import login_as


def test_horarios_owner_crud(client: TestClient, db_session: Session, admin_user):
    login_as(client, admin_user["email"], admin_user["password"])

    res = client.get("/api/v1/config/horarios")
    assert res.status_code == 200
    assert len(res.json()["dias"]) == 7

    payload = {
        "dias": [
            {"weekday": w, "cerrado": w >= 5, "opens_at": "20:00:00", "closes_at": "00:00:00"}
            for w in range(7)
        ]
    }
    put = client.put("/api/v1/config/horarios", json=payload)
    assert put.status_code == 200, put.text

    row = db_session.get(HorarioLocal, 0)
    assert row is not None
    assert row.opens_at == time(20, 0)


def test_public_tienda_respeta_horarios(client: TestClient, admin_user, producto_factory):
    login_as(client, admin_user["email"], admin_user["password"])
    client.put(
        "/api/v1/config/horarios",
        json={
            "dias": [
                {"weekday": w, "cerrado": True, "opens_at": None, "closes_at": None}
                for w in range(7)
            ]
        },
    )

    tienda = client.get("/api/v1/public/tienda")
    assert tienda.status_code == 200
    assert tienda.json()["abierto"] is False

    producto = producto_factory()
    pedido = client.post(
        "/api/v1/public/pedidos",
        json={
            "cliente": {"nombre": "X", "apellido": "Y", "email": "cerrado@test.com"},
            "items": [{"producto_id": producto.id, "cantidad": 1, "personalizacion": []}],
            "forma_pago_codigo": "EFECTIVO",
            "tipo_pedido": "PICKUP",
        },
    )
    assert pedido.status_code == 403
