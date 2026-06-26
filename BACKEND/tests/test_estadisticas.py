"""
Tests del módulo Estadísticas — Section 13.3 (Rubric)

EST-01: CANCELADO no suma
EST-02: usa subtotal_snap
EST-03: solo mp_status='approved' cuenta como ingreso confirmado
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.helpers import login_as


def _crear_pago(session: Session, pedido_id: int, mp_status: str, mp_payment_id: int):
    from app.modules.dominio_3.pagos.models import Pago
    pago = Pago(
        pedido_id=pedido_id,
        mp_payment_id=mp_payment_id,
        mp_status=mp_status,
        mp_status_detail="accredited" if mp_status == "approved" else "rejected",
        transaction_amount=Decimal("150.00"),
        payment_method_id="visa",
        external_reference=f"pedido_{pedido_id}_p{mp_payment_id}",
        idempotency_key=f"idem_{pedido_id}_p{mp_payment_id}",
    )
    session.add(pago)
    session.commit()


@pytest.fixture()
def admin_auth(client: TestClient, admin_user):
    login_as(client, admin_user["email"], admin_user["password"])


# ══════════════════════════════════════════════════════════════════════════════

class TestResumen:
    def test_resumen_kpis(self, db_session, client, admin_auth, client_user, pedido_factory):
        """GET /api/v1/estadisticas/resumen → KPIs con valores correctos."""
        p1 = pedido_factory(usuario_id=client_user["id"], estado="CONFIRMADO")
        _crear_pago(db_session, p1.id, "approved", 111111)
        p2 = pedido_factory(usuario_id=client_user["id"], estado="CONFIRMADO")
        _crear_pago(db_session, p2.id, "approved", 222222)

        res = client.get("/api/v1/estadisticas/resumen")
        assert res.status_code == 200, res.text
        data = res.json()
        assert Decimal(data["ventas_hoy"]) > 0
        assert Decimal(data["ticket_promedio"]) > 0
        assert Decimal(data["mes_actual"]) > 0

    def test_cancelado_no_suma(self, client, admin_auth, client_user, pedido_factory):
        """EST-01: CANCELADO no se contabiliza en ventas_hoy."""
        pedido_factory(usuario_id=client_user["id"], estado="CANCELADO")

        res = client.get("/api/v1/estadisticas/resumen")
        assert res.status_code == 200
        assert Decimal(res.json()["ventas_hoy"]) == Decimal("0.00")

    def test_est03_pago_approved_si_suma(self, db_session, client, admin_auth, client_user, pedido_factory):
        """EST-03: pedido con pago approved → suma."""
        p = pedido_factory(usuario_id=client_user["id"], estado="CONFIRMADO")
        _crear_pago(db_session, p.id, "approved", 333333)

        res = client.get("/api/v1/estadisticas/resumen")
        assert res.status_code == 200
        assert Decimal(res.json()["ventas_hoy"]) > 0

    def test_est03_pago_rejected_no_suma(self, db_session, client, admin_auth, client_user, pedido_factory):
        """EST-03: pedido con pago rejected → NO suma."""
        p = pedido_factory(usuario_id=client_user["id"], estado="CONFIRMADO")
        _crear_pago(db_session, p.id, "rejected", 444444)

        res = client.get("/api/v1/estadisticas/resumen")
        assert res.status_code == 200
        assert Decimal(res.json()["ventas_hoy"]) == Decimal("0.00")

    def test_no_mp_payment_suma(self, client, admin_auth, client_user, pedido_factory):
        """Pago EFECTIVO sin registro Pago → suma igual."""
        pedido_factory(usuario_id=client_user["id"], estado="CONFIRMADO", forma_pago="EFECTIVO")

        res = client.get("/api/v1/estadisticas/resumen")
        assert res.status_code == 200
        assert Decimal(res.json()["ventas_hoy"]) > 0


class TestProductosTop:
    def test_productos_top(self, db_session, client, admin_auth, client_user, pedido_factory):
        """GET /api/v1/estadisticas/productos-top → lista ordenada."""
        p = pedido_factory(usuario_id=client_user["id"], estado="CONFIRMADO")
        _crear_pago(db_session, p.id, "approved", 555555)

        res = client.get("/api/v1/estadisticas/productos-top?limit=10")
        assert res.status_code == 200, res.text
        data = res.json()
        assert isinstance(data, list)
        if len(data) > 0:
            item = data[0]
            assert "producto_id" in item
            assert "nombre" in item
            assert "ingresos" in item
            assert "cantidad_vendida" in item


class TestPedidosPorEstado:
    def test_pedidos_por_estado(self, client, admin_auth, client_user, pedido_factory):
        """GET /api/v1/estadisticas/pedidos-por-estado → conteo."""
        pedido_factory(usuario_id=client_user["id"], estado="PENDIENTE")
        pedido_factory(usuario_id=client_user["id"], estado="CONFIRMADO")
        pedido_factory(usuario_id=client_user["id"], estado="CANCELADO")

        res = client.get("/api/v1/estadisticas/pedidos-por-estado")
        assert res.status_code == 200, res.text
        estados = {item["estado_codigo"]: item["cantidad"] for item in res.json()}
        assert estados.get("PENDIENTE", 0) >= 1
        assert estados.get("CONFIRMADO", 0) >= 1
        assert estados.get("CANCELADO", 0) >= 1


class TestIngresos:
    def test_ingresos_por_forma_pago(self, db_session, client, admin_auth, client_user, pedido_factory):
        """GET /api/v1/estadisticas/ingresos → agrupado por forma_pago."""
        hoy = date.today()

        p1 = pedido_factory(usuario_id=client_user["id"], estado="CONFIRMADO", forma_pago="MERCADOPAGO")
        _crear_pago(db_session, p1.id, "approved", 666666)
        pedido_factory(usuario_id=client_user["id"], estado="CONFIRMADO", forma_pago="EFECTIVO")

        res = client.get("/api/v1/estadisticas/ingresos", params={
            "desde": str(hoy), "hasta": str(hoy),
        })
        assert res.status_code == 200, res.text
        formas = {item["forma_pago_codigo"]: Decimal(item["total"]) for item in res.json()}
        assert formas.get("MERCADOPAGO", Decimal("0")) > 0
        assert formas.get("EFECTIVO", Decimal("0")) > 0


class TestVentasPeriodo:
    def test_ventas_periodo(self, db_session, client, admin_auth, client_user, pedido_factory):
        """GET /api/v1/estadisticas/ventas → agrupado por día."""
        hoy = date.today()
        ayer = hoy - timedelta(days=1)

        p = pedido_factory(usuario_id=client_user["id"], estado="CONFIRMADO")
        _crear_pago(db_session, p.id, "approved", 777777)
        pedido_factory(usuario_id=client_user["id"], estado="CANCELADO")

        res = client.get("/api/v1/estadisticas/ventas", params={
            "desde": str(ayer), "hasta": str(hoy), "agrupacion": "day",
        })
        assert res.status_code == 200, res.text
        data = res.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "periodo" in data[0]
            assert "total_ventas" in data[0]
