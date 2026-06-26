"""
Tests del módulo Pagos — MercadoPago (con mocks)
"""

import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.helpers import login_as


@pytest.fixture()
def client_auth(client: TestClient, client_user):
    login_as(client, client_user["email"], client_user["password"])


@pytest.fixture()
def admin_auth(client: TestClient, admin_user):
    login_as(client, admin_user["email"], admin_user["password"])


def _crear_pedido_via_api(client, producto_factory, forma_pago="MERCADOPAGO", cantidad=1):
    """Crea un pedido via API (garantiza que pertenece al usuario logueado)."""
    prod = producto_factory()
    res = client.post("/api/v1/pedidos", json={
        "forma_pago_codigo": forma_pago,
        "items": [{"producto_id": prod.id, "cantidad": cantidad}],
    })
    assert res.status_code == 201, f"Crear pedido falló: {res.text}"
    return res.json()


# ══════════════════════════════════════════════════════════════════════════════

class TestCrearPago:
    def test_crear_pago_ok(self, client, client_auth, producto_factory):
        """POST /api/v1/pagos/crear con mock MP approved → 201."""
        pedido = _crear_pedido_via_api(client, producto_factory)

        mock_mp = {"status": 201, "response": {
            "id": 123456789, "status": "approved", "status_detail": "accredited",
            "payment_method_id": "visa", "transaction_amount": 150.0,
        }}
        with patch("mercadopago.SDK") as mock_sdk_class:
            mock_sdk = MagicMock()
            mock_sdk.payment.return_value.create.return_value = mock_mp
            mock_sdk_class.return_value = mock_sdk

            res = client.post("/api/v1/pagos/crear", json={
                "pedido_id": pedido["id"], "token": "tok_test",
                "payment_method_id": "visa", "installments": 1,
            })

        assert res.status_code == 201, res.text
        data = res.json()
        assert data["pedido_id"] == pedido["id"]
        assert data["mp_status"] == "approved"
        assert data["payment_method_id"] == "visa"

    def test_crear_pago_pedido_no_pendiente(self, client, client_auth, client_user, pedido_factory):
        """POST /api/v1/pagos/crear con pedido CONFIRMADO → 409."""
        pedido = pedido_factory(usuario_id=client_user["id"], estado="CONFIRMADO")

        res = client.post("/api/v1/pagos/crear", json={
            "pedido_id": pedido.id, "token": "tok_test",
            "payment_method_id": "visa", "installments": 1,
        })
        assert res.status_code == 409

    def test_crear_pago_pedido_ajeno(self, client, client_auth, admin_auth, producto_factory):
        """POST /api/v1/pagos/crear de pedido ajeno → 403."""
        # admin_auth ya nos logueó como admin — crear pedido
        pedido = _crear_pedido_via_api(client, producto_factory)

        # Cambiar a cliente
        login_as(client, "cliente@test.com", "Cliente1234!")
        res = client.post("/api/v1/pagos/crear", json={
            "pedido_id": pedido["id"], "token": "tok_test",
            "payment_method_id": "visa", "installments": 1,
        })
        assert res.status_code == 403

    def test_crear_pago_idempotencia(self, client, client_auth, producto_factory):
        """Dos pagos al mismo pedido → idempotencia retorna el pago existente."""
        pedido = _crear_pedido_via_api(client, producto_factory)

        mock_call = 0

        def mock_create(payment_data):
            nonlocal mock_call
            mock_call += 1
            return {"status": 201, "response": {
                "id": 100 + mock_call, "status": "pending",
                "status_detail": "pending_waiting_payment",
                "payment_method_id": payment_data.get("payment_method_id", "visa"),
                "transaction_amount": 150.0,
            }}

        with patch("mercadopago.SDK") as mock_sdk_class:
            mock_sdk = MagicMock()
            mock_sdk.payment.return_value.create.side_effect = mock_create
            mock_sdk_class.return_value = mock_sdk

            r1 = client.post("/api/v1/pagos/crear", json={
                "pedido_id": pedido["id"], "token": "tok_A",
                "payment_method_id": "visa", "installments": 1,
            })
            r2 = client.post("/api/v1/pagos/crear", json={
                "pedido_id": pedido["id"], "token": "tok_B",
                "payment_method_id": "master", "installments": 3,
            })

        assert r1.status_code == 201
        assert r2.status_code == 201
        # Idempotencia: el segundo pago retorna el mismo registro que el primero
        assert r1.json()["id"] == r2.json()["id"]


class TestWebhook:
    def test_webhook_aprueba_pago(self, db_session, client, client_auth, producto_factory):
        """Webhook con pago approved → avanza pedido a CONFIRMADO."""
        pedido = _crear_pedido_via_api(client, producto_factory)

        # Crear pago pendiente en BD (como si MP lo registró)
        from app.modules.dominio_3.pagos.models import Pago
        pago = Pago(
            pedido_id=pedido["id"], mp_payment_id=99999999, mp_status="pending",
            transaction_amount=Decimal("150.00"),
            external_reference=f"pedido_{pedido['id']}_wh",
            idempotency_key=f"idem_wh_{uuid.uuid4().hex[:16]}",
        )
        db_session.add(pago)
        db_session.commit()

        mock_get = {"status": 200, "response": {
            "id": 99999999, "status": "approved", "status_detail": "accredited",
            "payment_method_id": "visa", "transaction_amount": 150.0,
        }}
        with patch("mercadopago.SDK") as mock_sdk_class, \
             patch("app.modules.dominio_3.pagos.services.PagoService.verificar_firma_mp", return_value=True):
            mock_sdk = MagicMock()
            mock_sdk.payment.return_value.get.return_value = mock_get
            mock_sdk_class.return_value = mock_sdk

            res = client.post("/api/v1/pagos/webhook", json={
                "type": "payment", "data": {"id": 99999999},
            })

        assert res.status_code == 200, res.text
        assert res.json()["status"] == "ok"

        # Pedido debe estar CONFIRMADO
        res_pedido = client.get(f"/api/v1/pedidos/{pedido['id']}")
        assert res_pedido.json()["estado_codigo"] == "CONFIRMADO"

    def test_webhook_tipo_no_payment(self, client):
        """Webhook con type != payment → ignorado."""
        with patch("app.modules.dominio_3.pagos.services.PagoService.verificar_firma_mp", return_value=True):
            res = client.post("/api/v1/pagos/webhook", json={
                "type": "test", "data": {"id": 123},
            })
        assert res.status_code == 200
        assert res.json()["status"] == "ignored"


class TestConsultarPago:
    def test_consultar_pago_ok(self, db_session, client, client_auth, producto_factory):
        """GET /api/v1/pagos/{pedido_id} → 200."""
        pedido = _crear_pedido_via_api(client, producto_factory)

        from app.modules.dominio_3.pagos.models import Pago
        pago = Pago(
            pedido_id=pedido["id"], mp_payment_id=555555, mp_status="approved",
            mp_status_detail="accredited", transaction_amount=Decimal("150.00"),
            payment_method_id="visa",
            external_reference=f"pedido_{pedido['id']}_c",
            idempotency_key=f"idem_c_{uuid.uuid4().hex[:16]}",
        )
        db_session.add(pago)
        db_session.commit()

        res = client.get(f"/api/v1/pagos/{pedido['id']}")
        assert res.status_code == 200, res.text
        assert res.json()["mp_status"] == "approved"

    def test_consultar_pago_ajeno(self, client, client_auth, admin_auth, producto_factory):
        """GET /api/v1/pagos/{pedido_id} de otro → 403."""
        # admin_auth ya nos logueó como admin — crear pedido
        pedido = _crear_pedido_via_api(client, producto_factory)

        # Cambiar a cliente
        login_as(client, "cliente@test.com", "Cliente1234!")
        res = client.get(f"/api/v1/pagos/{pedido['id']}")
        assert res.status_code == 403
