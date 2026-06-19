from app.core.unit_of_work import UnitOfWork
from app.modules.estadisticas.repository import EstadisticasRepository


class EstadisticasUnitOfWork(UnitOfWork):
    """UoW de solo lectura para el módulo de estadísticas."""

    def __enter__(self) -> "EstadisticasUnitOfWork":
        super().__enter__()
        self.estadisticas = EstadisticasRepository(self._session)
        return self
