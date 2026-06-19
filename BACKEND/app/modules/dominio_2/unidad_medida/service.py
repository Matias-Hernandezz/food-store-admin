from app.modules.dominio_2.unidad_medida.repository import UnidadMedidaRepository
from app.modules.dominio_2.unidad_medida.schemas import UnidadMedidaRead


class UnidadMedidaService:
    """Servicio de solo lectura para unidades de medida."""

    def __init__(self, repo: UnidadMedidaRepository):
        self.repo = repo

    def listar(self) -> list[UnidadMedidaRead]:
        unidades = self.repo.get_all()
        return [UnidadMedidaRead.model_validate(u) for u in unidades]
