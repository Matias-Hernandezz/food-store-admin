from typing import Generator

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.deps import require_role
from .services import CategoriaService
from .schemas import CategoriaCreate, CategoriaUpdate, CategoriaRead, CategoriaList, ImagenCategoriaUpdate
from .unit_of_work import CategoriaUnitOfWork

router = APIRouter(prefix="/api/v1/categorias", tags=["Categorias"])


def get_categoria_uow(session: Session = Depends(get_session)) -> Generator[CategoriaUnitOfWork, None, None]:
    """Dependency: abre CategoriaUnitOfWork y lo cierra al finalizar el request."""
    with CategoriaUnitOfWork(session) as uow:
        yield uow


@router.post(
    "/",
    response_model=CategoriaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una categoría",
    dependencies=[Depends(require_role(["ADMIN"]))],
)
def create_categoria(
    data: CategoriaCreate,
    uow: CategoriaUnitOfWork = Depends(get_categoria_uow),
) -> CategoriaRead:
    svc = CategoriaService(uow)
    return svc.create(data)


@router.get(
    "/",
    response_model=CategoriaList,
    summary="Listar categorías activas (paginado)",
)
def list_categorias(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    incluir_eliminados: bool = Query(default=False),
    uow: CategoriaUnitOfWork = Depends(get_categoria_uow),
) -> CategoriaList:
    svc = CategoriaService(uow)
    return svc.get_all(offset=offset, limit=limit, incluir_eliminados=incluir_eliminados)


@router.get(
    "/{categoria_id}",
    response_model=CategoriaRead,
    summary="Obtener categoría por ID",
)
def get_categoria(
    categoria_id: int,
    uow: CategoriaUnitOfWork = Depends(get_categoria_uow),
) -> CategoriaRead:
    svc = CategoriaService(uow)
    return svc.get_by_id(categoria_id)


@router.put(
    "/{categoria_id}",
    response_model=CategoriaRead,
    summary="Actualizar categoría",
    dependencies=[Depends(require_role(["ADMIN"]))],
)
def update_categoria(
    categoria_id: int,
    data: CategoriaUpdate,
    uow: CategoriaUnitOfWork = Depends(get_categoria_uow),
) -> CategoriaRead:
    svc = CategoriaService(uow)
    return svc.update(categoria_id, data)


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete de categoría",
    dependencies=[Depends(require_role(["ADMIN"]))],
)
def delete_categoria(
    categoria_id: int,
    uow: CategoriaUnitOfWork = Depends(get_categoria_uow),
) -> None:
    svc = CategoriaService(uow)
    svc.soft_delete(categoria_id)


@router.patch(
    "/{categoria_id}/restaurar",
    response_model=CategoriaRead,
    summary="Restaurar categoría eliminada",
    dependencies=[Depends(require_role(["ADMIN"]))],
)
def restore_categoria(
    categoria_id: int,
    uow: CategoriaUnitOfWork = Depends(get_categoria_uow),
) -> CategoriaRead:
    svc = CategoriaService(uow)
    return svc.restore(categoria_id)


@router.patch(
    "/{categoria_id}/imagen",
    response_model=CategoriaRead,
    summary="Actualizar solo la imagen de una categoría",
    dependencies=[Depends(require_role(["ADMIN"]))],
)
def update_imagen_categoria(
    categoria_id: int,
    data: ImagenCategoriaUpdate,
    uow: CategoriaUnitOfWork = Depends(get_categoria_uow),
) -> CategoriaRead:
    svc = CategoriaService(uow)
    return svc.update(categoria_id, CategoriaUpdate(imagen_url=data.imagen_url))
