from sqlmodel import Session

from app.core.unit_of_work import UnitOfWork
from app.modules.dominio_2.unidad_medida.repository import UnidadMedidaRepository


class UnidadMedidaUnitOfWork(UnitOfWork):
    """Unit of Work para el módulo de unidades de medida (catálogo de solo lectura)."""

    def __init__(self, session: Session):
        super().__init__(session)
        self.unidades = UnidadMedidaRepository(session)
