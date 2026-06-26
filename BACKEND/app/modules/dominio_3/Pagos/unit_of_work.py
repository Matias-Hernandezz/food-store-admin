from app.core.unit_of_work import UnitOfWork
from app.modules.dominio_3.pagos.repository import PagoRepository
from app.modules.dominio_3.pedidos.repository import (
    PedidoRepository,
    HistorialRepository,
    DetallePedidoRepository,
)


class PagoUnitOfWork(UnitOfWork):
    """
    UoW específico para operaciones de pago.
    Incluye acceso a pagos, pedidos e historial porque
    al confirmar un pago se avanza el estado del pedido.
    """

    def __enter__(self) -> "PagoUnitOfWork":
        super().__enter__()
        self.pagos = PagoRepository(self._session)
        self.pedidos = PedidoRepository(self._session)
        self.historial = HistorialRepository(self._session)
        self.detalles = DetallePedidoRepository(self._session)
        return self
