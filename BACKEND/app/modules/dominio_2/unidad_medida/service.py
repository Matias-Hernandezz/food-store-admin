from app.modules.dominio_2.unidad_medida.unit_of_work import UnidadMedidaUnitOfWork
from app.modules.dominio_2.unidad_medida.schemas import UnidadMedidaRead


class UnidadMedidaService:
    """Servicio de solo lectura para unidades de medida."""

    def __init__(self, uow: UnidadMedidaUnitOfWork):
        self.uow = uow

    def listar(self) -> list[UnidadMedidaRead]:
        unidades = self.uow.unidades.get_all()
        return [UnidadMedidaRead.model_validate(u) for u in unidades]
