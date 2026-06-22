"""
Tests del módulo Pedidos — Section 13.3 (Rubric)

FSM 5 estados: PENDIENTE → CONFIRMADO → EN_PREP → ENTREGADO / CANCELADO
"""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from tests.helpers import login_as


@pytest.fixture()
def admin_auth(client: TestClient, admin_user):
    """Helper: loguea como admin."""
    login_as(client, admin_user["email"], admin_user["password"])


@pytest.fixture()
def client_auth(client: TestClient, client_user):
    """Helper: loguea como cliente."""
    login_as(client, client_user["email"], client_user["password"])


# ══════════════════════════════════════════════════════════════════════════════
# CREAR PEDIDO
# ══════════════════════════════════════════════════════════════════════════════

class TestCrearPedido:
    def test_crear_pedido_ok(self, client: TestClient, client_auth, client_user, producto_factory):
        """POST /api/v1/pedidos → 201, estado PENDIENTE, costo_envio=50.00."""
        prod = producto_factory(nombre="Hamburguesa", precio=Decimal("150.00"), stock=20)

        res = client.post("/api/v1/pedidos", json={
            "forma_pago_codigo": "MERCADOPAGO",
            "items": [{"producto_id": prod.id, "cantidad": 2}],
        })
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["estado_codigo"] == "PENDIENTE"
        assert Decimal(data["subtotal"]) == Decimal("300.00")
        assert Decimal(data["costo_envio"]) == Decimal("50.00")
        assert Decimal(data["total"]) == Decimal("350.00")
        assert len(data["detalles"]) == 1
        assert data["detalles"][0]["nombre_snapshot"] == "Hamburguesa"
        assert Decimal(data["detalles"][0]["precio_snapshot"]) == Decimal("150.00")

    def test_crear_pedido_sin_items(self, client: TestClient, client_auth):
        """POST /api/v1/pedidos sin items → 422."""
        res = client.post("/api/v1/pedidos", json={
            "forma_pago_codigo": "MERCADOPAGO", "items": [],
        })
        assert res.status_code == 422

    def test_crear_pedido_producto_no_disponible(self, client: TestClient, client_auth, producto_factory):
        """POST /api/v1/pedidos con producto.disponible=False → 400."""
        prod = producto_factory(nombre="NoDisp", disponible=False)

        res = client.post("/api/v1/pedidos", json={
            "forma_pago_codigo": "MERCADOPAGO",
            "items": [{"producto_id": prod.id, "cantidad": 1}],
        })
        assert res.status_code == 400

    def test_crear_pedido_stock_insuficiente(self, client: TestClient, client_auth, producto_factory):
        """POST /api/v1/pedidos con stock=0 → 400 (stock insuficiente)."""
        prod = producto_factory(nombre="SinStock", stock=0, disponible=True)

        res = client.post("/api/v1/pedidos", json={
            "forma_pago_codigo": "MERCADOPAGO",
            "items": [{"producto_id": prod.id, "cantidad": 1}],
        })
        assert res.status_code == 400
        assert "stock" in res.json()["detail"].lower()

    def test_crear_pedido_forma_pago_invalida(self, client: TestClient, client_auth, producto_factory):
        """POST /api/v1/pedidos con forma de pago inexistente → 400."""
        prod = producto_factory()
        res = client.post("/api/v1/pedidos", json={
            "forma_pago_codigo": "INEXISTENTE",
            "items": [{"producto_id": prod.id, "cantidad": 1}],
        })
        assert res.status_code == 400

    def test_crear_pedido_sin_auth(self, client: TestClient, producto_factory):
        """POST /api/v1/pedidos sin autenticación → 401."""
        prod = producto_factory()
        res = client.post("/api/v1/pedidos", json={
            "forma_pago_codigo": "MERCADOPAGO",
            "items": [{"producto_id": prod.id, "cantidad": 1}],
        })
        assert res.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
# FSM — TRANSICIONES DE ESTADO
# ══════════════════════════════════════════════════════════════════════════════

class TestFSM:
    def test_avanzar_estado_valido(self, client: TestClient, admin_auth, client_user, pedido_factory):
        """PATCH estado → PENDIENTE a CONFIRMADO → 200. Historial append-only."""
        pedido = pedido_factory(usuario_id=client_user["id"], estado="PENDIENTE")

        res = client.patch(f"/api/v1/pedidos/{pedido.id}/estado", json={
            "nuevo_estado": "CONFIRMADO",
        })
        assert res.status_code == 200, res.text
        assert res.json()["estado_codigo"] == "CONFIRMADO"

        # Verificar historial (RN-02: primer registro estado_desde=None)
        res_hist = client.get(f"/api/v1/pedidos/{pedido.id}/historial")
        assert res_hist.status_code == 200
        historial = res_hist.json()
        assert len(historial) == 2
        assert historial[0]["estado_desde"] is None
        assert historial[0]["estado_hacia"] == "PENDIENTE"
        assert historial[1]["estado_desde"] == "PENDIENTE"
        assert historial[1]["estado_hacia"] == "CONFIRMADO"

    def test_avanzar_estado_terminal_rechazado(self, client: TestClient, admin_auth, client_user, pedido_factory):
        """PATCH desde ENTREGADO (terminal) → 403/422 (RN-01)."""
        pedido = pedido_factory(usuario_id=client_user["id"], estado="ENTREGADO")

        res = client.patch(f"/api/v1/pedidos/{pedido.id}/estado", json={
            "nuevo_estado": "EN_PREP",
        })
        assert res.status_code in (403, 422), res.text

    def test_cancelar_requiere_motivo(self, client: TestClient, admin_auth, client_user, pedido_factory):
        """PATCH → CANCELADO sin motivo → 422 (RN-05)."""
        pedido = pedido_factory(usuario_id=client_user["id"], estado="PENDIENTE")

        res = client.patch(f"/api/v1/pedidos/{pedido.id}/estado", json={
            "nuevo_estado": "CANCELADO",
        })
        assert res.status_code == 422

    def test_cancelar_con_motivo_ok(self, client: TestClient, admin_auth, client_user, pedido_factory):
        """PATCH → CANCELADO con motivo → 200."""
        pedido = pedido_factory(usuario_id=client_user["id"], estado="PENDIENTE")

        res = client.patch(f"/api/v1/pedidos/{pedido.id}/estado", json={
            "nuevo_estado": "CANCELADO",
            "motivo": "Producto agotado",
        })
        assert res.status_code == 200, res.text
        assert res.json()["estado_codigo"] == "CANCELADO"

    def test_cliente_cancela_propio(self, client: TestClient, client_auth, client_user, pedido_factory):
        """DELETE /api/v1/pedidos/{id} como propietario → 200."""
        pedido = pedido_factory(usuario_id=client_user["id"], estado="PENDIENTE")

        res = client.request("DELETE", f"/api/v1/pedidos/{pedido.id}", json={
            "nuevo_estado": "CANCELADO",
            "motivo": "Me arrepentí",
        })
        assert res.status_code == 200, res.text
        assert res.json()["estado_codigo"] == "CANCELADO"

    def test_cliente_no_cancela_ajeno(self, client: TestClient, client_auth, admin_user, pedido_factory):
        """DELETE como cliente de un pedido ajeno → 403."""
        pedido = pedido_factory(usuario_id=admin_user["id"], estado="PENDIENTE")

        res = client.request("DELETE", f"/api/v1/pedidos/{pedido.id}", json={
            "nuevo_estado": "CANCELADO", "motivo": "No es mío",
        })
        assert res.status_code == 403

    def test_historial_append_only(self, client: TestClient, admin_auth, client_user, pedido_factory):
        """3 transiciones → 4 registros ordenados ASC (RN-03)."""
        pedido = pedido_factory(usuario_id=client_user["id"], estado="PENDIENTE")

        for estado in ["CONFIRMADO", "EN_PREP", "ENTREGADO"]:
            res = client.patch(f"/api/v1/pedidos/{pedido.id}/estado", json={
                "nuevo_estado": estado,
            })
            assert res.status_code == 200, f"Falló en {estado}: {res.text}"

        res_hist = client.get(f"/api/v1/pedidos/{pedido.id}/historial")
        assert res_hist.status_code == 200
        historial = res_hist.json()
        assert len(historial) == 4
        created_ats = [h["created_at"] for h in historial]
        assert created_ats == sorted(created_ats), "Historial debe estar ordenado ASC"


# ══════════════════════════════════════════════════════════════════════════════
# LISTAR PEDIDOS
# ══════════════════════════════════════════════════════════════════════════════

class TestListarPedidos:
    def test_listar_cliente_solo_propios(self, client: TestClient, client_auth, client_user, admin_user, pedido_factory):
        """GET /api/v1/pedidos como CLIENT → solo ve sus pedidos."""
        pedido_factory(usuario_id=client_user["id"], estado="PENDIENTE")
        pedido_factory(usuario_id=client_user["id"], estado="CONFIRMADO")

        # Cambiar a admin para crear pedido del admin
        login_as(client, admin_user["email"], admin_user["password"])
        pedido_factory(usuario_id=admin_user["id"], estado="PENDIENTE")

        # Volver a cliente para el listado
        login_as(client, client_user["email"], client_user["password"])
        res = client.get("/api/v1/pedidos")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 2
        for p in data["data"]:
            assert p["usuario_id"] == client_user["id"]

    def test_listar_admin_ve_todos(self, client: TestClient, admin_auth, client_user, pedido_factory):
        """GET /api/v1/pedidos como ADMIN → ve todos."""
        pedido_factory(usuario_id=client_user["id"], estado="PENDIENTE")
        pedido_factory(usuario_id=client_user["id"], estado="CONFIRMADO")
        pedido_factory(usuario_id=client_user["id"], estado="PENDIENTE")

        res = client.get("/api/v1/pedidos")
        assert res.status_code == 200
        assert res.json()["total"] == 3
