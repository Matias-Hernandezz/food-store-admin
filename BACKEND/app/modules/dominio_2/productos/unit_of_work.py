from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.dominio_2.productos.repository import ProductoRepository
from app.modules.dominio_2.categorias.repository import CategoriaRepository
from app.modules.dominio_2.ingredientes.repository import IngredienteRepository
from app.modules.dominio_2.unidad_medida.repository import UnidadMedidaRepository

class ProductoUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.productos = ProductoRepository(session)
        self.categorias = CategoriaRepository(session)
        self.ingredientes = IngredienteRepository(session)
        self.unidad_medida = UnidadMedidaRepository(session)