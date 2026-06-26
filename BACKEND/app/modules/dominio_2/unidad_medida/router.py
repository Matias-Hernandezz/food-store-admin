from typing import Generator

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.db import get_session
from app.modules.dominio_2.unidad_medida.schemas import UnidadMedidaRead
from app.modules.dominio_2.unidad_medida.service import UnidadMedidaService
from app.modules.dominio_2.unidad_medida.unit_of_work import UnidadMedidaUnitOfWork

router = APIRouter(prefix="/api/v1/unidades-medida", tags=["Unidades de Medida"])


def get_unidad_medida_uow(
    session: Session = Depends(get_session),
) -> Generator[UnidadMedidaUnitOfWork, None, None]:
    with UnidadMedidaUnitOfWork(session) as uow:
        yield uow


@router.get("/", response_model=list[UnidadMedidaRead])
def listar_unidades(uow: UnidadMedidaUnitOfWork = Depends(get_unidad_medida_uow)):
    with uow:
        return UnidadMedidaService(uow).listar()
