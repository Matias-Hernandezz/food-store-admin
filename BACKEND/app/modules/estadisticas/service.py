from datetime import date

from app.modules.estadisticas.schemas import (
    ResumenResponse,
    VentasPeriodoItem,
    ProductoTopItem,
    PedidosEstadoItem,
    IngresosItem,
)
from app.modules.estadisticas.unit_of_work import EstadisticasUnitOfWork


class EstadisticasService:
    def __init__(self, uow: EstadisticasUnitOfWork):
        self.uow = uow

    def resumen(self) -> ResumenResponse:
        repo = self.uow.estadisticas
        return ResumenResponse(
            ventas_hoy=repo.ventas_hoy(),
            ticket_promedio=repo.ticket_promedio(),
            pedidos_activos=repo.pedidos_activos(),
            mes_actual=repo.mes_actual(),
        )

    def ventas(self, desde: date, hasta: date, agrupacion: str = "day") -> list[VentasPeriodoItem]:
        data = self.uow.estadisticas.ventas_periodo(desde, hasta, agrupacion)
        return [VentasPeriodoItem(**item) for item in data]

    def productos_top(self, limit: int = 10) -> list[ProductoTopItem]:
        data = self.uow.estadisticas.productos_top(limit)
        return [ProductoTopItem(**item) for item in data]

    def pedidos_por_estado(self) -> list[PedidosEstadoItem]:
        data = self.uow.estadisticas.pedidos_por_estado()
        return [PedidosEstadoItem(**item) for item in data]

    def ingresos(self, desde: date, hasta: date) -> list[IngresosItem]:
        data = self.uow.estadisticas.ingresos_por_forma_pago(desde, hasta)
        return [IngresosItem(**item) for item in data]
