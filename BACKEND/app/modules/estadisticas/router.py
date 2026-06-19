from datetime import date
from typing import Generator

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.db import get_session
from app.core.deps import require_role
from app.modules.estadisticas.schemas import (
    ResumenResponse,
    VentasPeriodoItem,
    ProductoTopItem,
    PedidosEstadoItem,
    IngresosItem,
)
from app.modules.estadisticas.service import EstadisticasService
from app.modules.estadisticas.unit_of_work import EstadisticasUnitOfWork

router = APIRouter(
    prefix="/api/v1/estadisticas",
    tags=["Estadísticas"],
    dependencies=[Depends(require_role(["ADMIN"]))],
)


def get_estadisticas_uow(
    session: Session = Depends(get_session),
) -> Generator[EstadisticasUnitOfWork, None, None]:
    with EstadisticasUnitOfWork(session) as uow:
        yield uow


@router.get("/resumen", response_model=ResumenResponse)
def resumen(uow: EstadisticasUnitOfWork = Depends(get_estadisticas_uow)):
    with uow:
        return EstadisticasService(uow).resumen()


@router.get("/ventas", response_model=list[VentasPeriodoItem])
def ventas(
    desde: date = Query(...),
    hasta: date = Query(...),
    agrupacion: str = Query("day", pattern="^(day|week|month)$"),
    uow: EstadisticasUnitOfWork = Depends(get_estadisticas_uow),
):
    with uow:
        return EstadisticasService(uow).ventas(desde, hasta, agrupacion)


@router.get("/productos-top", response_model=list[ProductoTopItem])
def productos_top(
    limit: int = Query(10, ge=1, le=50),
    uow: EstadisticasUnitOfWork = Depends(get_estadisticas_uow),
):
    with uow:
        return EstadisticasService(uow).productos_top(limit)


@router.get("/pedidos-por-estado", response_model=list[PedidosEstadoItem])
def pedidos_por_estado(uow: EstadisticasUnitOfWork = Depends(get_estadisticas_uow)):
    with uow:
        return EstadisticasService(uow).pedidos_por_estado()


@router.get("/ingresos", response_model=list[IngresosItem])
def ingresos(
    desde: date = Query(...),
    hasta: date = Query(...),
    uow: EstadisticasUnitOfWork = Depends(get_estadisticas_uow),
):
    with uow:
        return EstadisticasService(uow).ingresos(desde, hasta)
