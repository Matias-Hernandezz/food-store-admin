"""Webhook Mercado Pago por slug (/webhooks/mp/{slug})."""

import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.control.models import Tenant, TenantStatus
from app.control.db import get_control_engine
from tests.conftest import test_engine
from tests.helpers import login_as
from tests.test_pagos import _crear_pedido_via_api


@pytest.fixture()
def control_schema():
    Tenant.metadata.create_all(test_engine)
    yield
    Tenant.metadata.drop_all(test_engine)


@pytest.fixture()
def mp_tenant_slug(control_schema):
    with Session(get_control_engine()) as session:
        session.add(
            Tenant(
                slug="burger",
                nombre="Burger Test",
                estado=TenantStatus.ACTIVE.value,
                db_name="foodstore_test",
                mp_access_token="TEST-TENANT-MP",
                mp_webhook_secret="whsec_test",
            )
        )
        session.commit()
    return "burger"


@pytest.fixture()
def client_auth(client: TestClient, client_user):
    login_as(client, client_user["email"], client_user["password"])


def test_webhook_por_slug_confirma_pedido(
    client: TestClient,
    client_auth,
    producto_factory,
    db_session: Session,
    mp_tenant_slug: str,
):
    pedido = _crear_pedido_via_api(client, producto_factory)

    from app.modules.dominio_3.pagos.models import Pago

    pago = Pago(
        pedido_id=pedido["id"],
        mp_payment_id=88888888,
        mp_status="pending",
        transaction_amount=Decimal("150.00"),
        external_reference=f"pedido_{pedido['id']}_slug",
        idempotency_key=f"idem_slug_{uuid.uuid4().hex[:16]}",
    )
    db_session.add(pago)
    db_session.commit()

    mock_get = {
        "status": 200,
        "response": {
            "id": 88888888,
            "status": "approved",
            "status_detail": "accredited",
            "payment_method_id": "visa",
            "transaction_amount": 150.0,
        },
    }

    with patch("mercadopago.SDK") as mock_sdk_class, patch(
        "app.modules.dominio_3.pagos.services.PagoService.verificar_firma_mp",
        return_value=True,
    ):
        mock_sdk = MagicMock()
        mock_sdk.payment.return_value.get.return_value = mock_get
        mock_sdk_class.return_value = mock_sdk

        res = client.post(
            f"/webhooks/mp/{mp_tenant_slug}",
            json={"type": "payment", "data": {"id": 88888888}},
            headers={"x-signature": "ts=1,v1=abc", "x-request-id": "req-1"},
        )

    assert res.status_code == 200, res.text
    res_pedido = client.get(f"/api/v1/pedidos/{pedido['id']}")
    assert res_pedido.json()["estado_codigo"] == "CONFIRMADO"


def test_webhook_slug_sin_mp_config(client: TestClient, control_schema):
    with Session(get_control_engine()) as session:
        session.add(
            Tenant(
                slug="sinmp",
                nombre="Sin MP",
                estado=TenantStatus.ACTIVE.value,
                db_name="foodstore_test",
            )
        )
        session.commit()

    res = client.post(
        "/webhooks/mp/sinmp",
        json={"type": "payment", "data": {"id": 1}},
    )
    assert res.status_code == 404
