from sqlmodel import Session
from app.core.repository import BaseRepository
from app.modules.dominio_2.unidad_medida.models import UnidadMedida


class UnidadMedidaRepository(BaseRepository[UnidadMedida]):
    def __init__(self, session: Session):
        super().__init__(session, UnidadMedida)
