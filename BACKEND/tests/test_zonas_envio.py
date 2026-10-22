"""Zonas de envío y mínimo de pedido."""

from decimal import Decimal

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.modules.local_config.models import ZonaEnvio
from tests.helpers import login_as


def test_cotizar_y_pedido_minimo(
    client: TestClient,
    db_session: Session,
    admin_user,
    client_user,
    pedido_factory,
):
    db_session.add(
        ZonaEnvio(
            nombre="Centro",
            ciudad_match="Rosario",
            costo_envio=Decimal("80"),
            pedido_minimo=Decimal("500"),
            activa=True,
            orden=1,
        )
    )
    db_session.commit()

    cot = client.post(
        "/api/v1/public/envio/cotizar",
        json={"subtotal": 400, "ciudad": "Rosario"},
    )
    assert cot.status_code == 200
    body = cot.json()
    assert body["costo_envio"] == 80.0
    assert body["alcanza_minimo"] is False

    cot_ok = client.post(
        "/api/v1/public/envio/cotizar",
        json={"subtotal": 600, "ciudad": "Rosario"},
    )
    assert cot_ok.json()["alcanza_minimo"] is True


def test_admin_guardar_zonas(client: TestClient, db_session: Session, admin_user):
    login_as(client, admin_user["email"], admin_user["password"])
    payload = {
        "zonas": [
            {
                "nombre": "General",
                "ciudad_match": None,
                "costo_envio": 50,
                "pedido_minimo": 0,
                "activa": True,
                "orden": 0,
            },
            {
                "nombre": "Norte",
                "ciudad_match": "Córdoba",
                "costo_envio": 120,
                "pedido_minimo": 1000,
                "activa": True,
                "orden": 1,
            },
        ]
    }
    res = client.put("/api/v1/config/zonas-envio", json=payload)
    assert res.status_code == 200, res.text
    assert len(res.json()["zonas"]) == 2
