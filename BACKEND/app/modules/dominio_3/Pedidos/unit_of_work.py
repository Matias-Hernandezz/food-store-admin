from app.modules.dominio_2.productos.repository import ProductoRepository
from app.core.unit_of_work import UnitOfWork
from app.modules.dominio_3.pagos.repository import PagoRepository
from .repository import PedidoRepository, DetallePedidoRepository, HistorialRepository, FormaPagoRepository, EstadoPedidoRepository

class PedidoUnitOfWork(UnitOfWork):
    def __enter__(self):
        super().__enter__()
        self.pedidos = PedidoRepository(self._session)
        self.detalles = DetallePedidoRepository(self._session)
        self.historial = HistorialRepository(self._session)
        self.formas_pago = FormaPagoRepository(self._session)
        self.estados = EstadoPedidoRepository(self._session)
        self.productos = ProductoRepository(self._session)
        self.pagos = PagoRepository(self._session)
        return self
