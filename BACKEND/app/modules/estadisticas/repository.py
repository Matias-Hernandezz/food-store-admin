from datetime import date, datetime, time, timedelta
from decimal import Decimal
from sqlalchemy import or_
from sqlmodel import Session, select, func, text
from app.modules.dominio_3.pedidos.models import Pedido, DetallePedido
from app.modules.dominio_3.pagos.models import Pago


def _arg_desde(desde: date) -> datetime:
    """Convierte fecha ARG a datetime UTC: 2026-06-21 00:00 ARG = UTC 03:00."""
    return datetime.combine(desde, time(3, 0, 0))


def _arg_hasta(hasta: date) -> datetime:
    """Día siguiente ARG a datetime UTC: exclusivo (<)."""
    return datetime.combine(hasta + timedelta(days=1), time(3, 0, 0))


def _ingresos_filtro():
    """EST-01 + EST-03: excluye CANCELADO y solo cuenta MP approved."""
    return or_(
        Pago.mp_status == "approved",  # pago MP confirmado
        Pago.id == None,               # pago no-MP (EFECTIVO, TRANSFERENCIA)
    )


class EstadisticasRepository:
    def __init__(self, session: Session):
        self.session = session

    # ── KPI helpers ───────────────────────────────────────────────────────

    def ventas_hoy(self) -> Decimal:
        """EST-01: excluye CANCELADO. EST-03: solo pagos approved."""
        hoy = date.today()
        result = self.session.exec(
            select(func.coalesce(func.sum(Pedido.total), 0))
            .outerjoin(Pago, Pago.pedido_id == Pedido.id)
            .where(Pedido.created_at >= _arg_desde(hoy))
            .where(Pedido.created_at < _arg_hasta(hoy))
            .where(Pedido.estado_codigo != "CANCELADO")
            .where(_ingresos_filtro())
        ).one()
        return Decimal(str(result))

    def ticket_promedio(self) -> Decimal:
        result = self.session.exec(
            select(func.coalesce(func.avg(Pedido.total), 0))
            .outerjoin(Pago, Pago.pedido_id == Pedido.id)
            .where(Pedido.estado_codigo != "CANCELADO")
            .where(_ingresos_filtro())
        ).one()
        # EST-04: mantener Decimal sin pasar por float
        val = Decimal(str(result))
        return val.quantize(Decimal("0.01"))

    def pedidos_activos(self) -> int:
        result = self.session.exec(
            select(func.count(Pedido.id))
            .where(Pedido.estado_codigo.in_(["PENDIENTE", "CONFIRMADO", "EN_PREP"]))
        ).one()
        return result

    def mes_actual(self) -> Decimal:
        """Total facturado en el mes actual."""
        hoy = date.today()
        inicio_mes = hoy.replace(day=1)
        result = self.session.exec(
            select(func.coalesce(func.sum(Pedido.total), 0))
            .outerjoin(Pago, Pago.pedido_id == Pedido.id)
            .where(Pedido.created_at >= _arg_desde(inicio_mes))
            .where(Pedido.estado_codigo != "CANCELADO")
            .where(_ingresos_filtro())
        ).one()
        return Decimal(str(result))

    # ── Ventas por período ────────────────────────────────────────────────

    def ventas_periodo(self, desde: date, hasta: date, agrupacion: str):
        trunc = text(f"DATE_TRUNC('{agrupacion}', pedido.created_at - INTERVAL '3 hours')")
        rows = self.session.exec(
            select(
                func.to_char(trunc, "YYYY-MM-DD").label("periodo"),
                func.sum(Pedido.total).label("total_ventas"),
                func.count(Pedido.id).label("cantidad_pedidos"),
            )
            .outerjoin(Pago, Pago.pedido_id == Pedido.id)
            .where(Pedido.created_at >= _arg_desde(desde))
            .where(Pedido.created_at < _arg_hasta(hasta))
            .where(Pedido.estado_codigo != "CANCELADO")
            .where(_ingresos_filtro())
            .group_by(trunc)
            .order_by(trunc)
        ).all()
        return [
            {
                "periodo": r.periodo,
                "total_ventas": Decimal(str(r.total_ventas)),
                "cantidad_pedidos": r.cantidad_pedidos,
            }
            for r in rows
        ]

    # ── Top productos ─────────────────────────────────────────────────────

    def productos_top(self, limit: int = 10):
        """EST-02: usa subtotal del DetallePedido (snapshot inmutable)."""
        rows = self.session.exec(
            select(
                DetallePedido.producto_id,
                DetallePedido.nombre_snapshot,
                func.sum(DetallePedido.subtotal).label("ingresos"),
                func.sum(DetallePedido.cantidad).label("cantidad_vendida"),
            )
            .join(Pedido, DetallePedido.pedido_id == Pedido.id)
            .outerjoin(Pago, Pago.pedido_id == Pedido.id)
            .where(Pedido.estado_codigo != "CANCELADO")
            .where(_ingresos_filtro())
            .group_by(DetallePedido.producto_id, DetallePedido.nombre_snapshot)
            .order_by(func.sum(DetallePedido.subtotal).desc())
            .limit(limit)
        ).all()
        return [
            {
                "producto_id": r.producto_id,
                "nombre": r.nombre_snapshot,
                "ingresos": Decimal(str(r.ingresos)),
                "cantidad_vendida": r.cantidad_vendida,
            }
            for r in rows
        ]

    # ── Pedidos por estado ────────────────────────────────────────────────

    def pedidos_por_estado(self):
        """Conteo simple por estado — no requiere filtro de ingresos."""
        rows = self.session.exec(
            select(
                Pedido.estado_codigo,
                func.count(Pedido.id).label("cantidad"),
            ).group_by(Pedido.estado_codigo)
        ).all()
        return [
            {"estado_codigo": r.estado_codigo, "cantidad": r.cantidad}
            for r in rows
        ]

    # ── Ingresos por forma de pago ────────────────────────────────────────

    def ingresos_por_forma_pago(self, desde: date, hasta: date):
        """EST-03: solo ingresos confirmados (MP approved o no-MP)."""
        rows = self.session.exec(
            select(
                Pedido.forma_pago_codigo,
                func.sum(Pedido.total).label("total"),
                func.count(Pedido.id).label("cantidad"),
            )
            .outerjoin(Pago, Pago.pedido_id == Pedido.id)
            .where(Pedido.created_at >= _arg_desde(desde))
            .where(Pedido.created_at < _arg_hasta(hasta))
            .where(Pedido.estado_codigo != "CANCELADO")
            .where(_ingresos_filtro())
            .group_by(Pedido.forma_pago_codigo)
        ).all()
        return [
            {
                "forma_pago_codigo": r.forma_pago_codigo,
                "total": Decimal(str(r.total)),
                "cantidad": r.cantidad,
            }
            for r in rows
        ]
