from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.db import get_session
from app.modules.dominio_2.unidad_medida.repository import UnidadMedidaRepository
from app.modules.dominio_2.unidad_medida.schemas import UnidadMedidaRead
from app.modules.dominio_2.unidad_medida.service import UnidadMedidaService

router = APIRouter(prefix="/api/v1/unidades-medida", tags=["Unidades de Medida"])


@router.get("/", response_model=list[UnidadMedidaRead])
def listar_unidades(session: Session = Depends(get_session)):
    repo = UnidadMedidaRepository(session)
    return UnidadMedidaService(repo).listar()
