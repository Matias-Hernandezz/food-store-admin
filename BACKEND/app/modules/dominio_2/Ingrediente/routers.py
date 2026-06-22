from typing import Generator

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.deps import require_role
from app.modules.dominio_2.Ingrediente.services import IngredienteService
from app.modules.dominio_2.Ingrediente.schemas import IngredienteCreate, IngredienteUpdate, IngredienteRead, IngredienteList
from app.modules.dominio_2.Ingrediente.unit_of_work import IngredienteUnitOfWork

router = APIRouter(prefix="/api/v1/ingredientes", tags=["Ingredientes"])


def get_ingrediente_uow(session: Session = Depends(get_session)) -> Generator[IngredienteUnitOfWork, None, None]:
    """Dependency: abre IngredienteUnitOfWork y lo cierra al finalizar el request."""
    with IngredienteUnitOfWork(session) as uow:
        yield uow


@router.post(
    "/",
    response_model=IngredienteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un ingrediente",
    dependencies=[Depends(require_role(["ADMIN"]))],
)
def create_ingrediente(
    data: IngredienteCreate,
    uow: IngredienteUnitOfWork = Depends(get_ingrediente_uow),
) -> IngredienteRead:
    svc = IngredienteService(uow)
    return svc.create(data)


@router.get(
    "/",
    response_model=IngredienteList,
    summary="Listar ingredientes activos (paginado)",
)
def list_ingredientes(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    incluir_eliminados: bool = Query(default=False),
    uow: IngredienteUnitOfWork = Depends(get_ingrediente_uow),
) -> IngredienteList:
    svc = IngredienteService(uow)
    return svc.get_all(offset=offset, limit=limit, incluir_eliminados=incluir_eliminados)


@router.get(
    "/{ingrediente_id}",
    response_model=IngredienteRead,
    summary="Obtener ingrediente por ID",
)
def get_ingrediente(
    ingrediente_id: int,
    uow: IngredienteUnitOfWork = Depends(get_ingrediente_uow),
) -> IngredienteRead:
    svc = IngredienteService(uow)
    return svc.get_by_id(ingrediente_id)


@router.put(
    "/{ingrediente_id}",
    response_model=IngredienteRead,
    summary="Actualizar ingrediente",
    dependencies=[Depends(require_role(["ADMIN"]))],
)
def update_ingrediente(
    ingrediente_id: int,
    data: IngredienteUpdate,
    uow: IngredienteUnitOfWork = Depends(get_ingrediente_uow),
) -> IngredienteRead:
    svc = IngredienteService(uow)
    return svc.update(ingrediente_id, data)


@router.delete(
    "/{ingrediente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar ingrediente",
    dependencies=[Depends(require_role(["ADMIN"]))],
)
def delete_ingrediente(
    ingrediente_id: int,
    uow: IngredienteUnitOfWork = Depends(get_ingrediente_uow),
) -> None:
    svc = IngredienteService(uow)
    svc.delete(ingrediente_id)


@router.patch(
    "/{ingrediente_id}/restaurar",
    response_model=IngredienteRead,
    summary="Restaurar ingrediente eliminado",
    dependencies=[Depends(require_role(["ADMIN"]))],
)
def restore_ingrediente(
    ingrediente_id: int,
    uow: IngredienteUnitOfWork = Depends(get_ingrediente_uow),
) -> IngredienteRead:
    svc = IngredienteService(uow)
    return svc.restore(ingrediente_id)
