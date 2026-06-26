from decimal import Decimal
from typing import Generator, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.deps import require_role
from app.modules.dominio_2.productos.schemas import (
    DisponibilidadUpdate,
    ImagenesProductoUpdate,
    ProductoCreate,
    ProductoIngredienteCreate,
    ProductoIngredienteRead,
    ProductoList,
    ProductoRead,
    ProductoUpdate,
)
from app.modules.dominio_2.productos.services import ProductoService
from app.modules.dominio_2.productos.unit_of_work import ProductoUnitOfWork

router = APIRouter(prefix="/api/v1/productos", tags=["Productos"])


def get_producto_uow(session: Session = Depends(get_session)) -> Generator[ProductoUnitOfWork, None, None]:
    """Dependency: abre ProductoUnitOfWork y lo cierra al finalizar el request."""
    with ProductoUnitOfWork(session) as uow:
        yield uow


# ── CRUD ────────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(["ADMIN"]))],
)
def create_producto(data: ProductoCreate, uow: ProductoUnitOfWork = Depends(get_producto_uow)):
    with uow:
        return ProductoService(uow).create(data)


@router.get("/", response_model=ProductoList)
def list_productos(
    page: int = Query(default=1, ge=1, description="Número de página"),
    size: int = Query(default=20, ge=1, le=100, description="Registros por página"),
    categoria: Optional[int] = Query(default=None, description="Filtrar por categoría"),
    disponible: Optional[bool] = Query(default=None, description="Filtrar por disponibilidad"),
    search: Optional[str] = Query(default=None, description="Buscar por nombre o descripción"),
    precio_min: Optional[Decimal] = Query(default=None, description="Precio mínimo"),
    precio_max: Optional[Decimal] = Query(default=None, description="Precio máximo"),
    en_stock: bool = Query(default=False, description="Solo productos con stock disponible"),
    orden: Optional[str] = Query(default=None, description="Orden: precio_asc, precio_desc, nombre"),
    incluir_eliminados: bool = Query(default=False, description="Incluir productos eliminados"),
    uow: ProductoUnitOfWork = Depends(get_producto_uow),
):
    with uow:
        return ProductoService(uow).get_all(
            offset=(page - 1) * size, limit=size,
            categoria_id=categoria,
            disponible=disponible,
            search=search,
            precio_min=precio_min,
            precio_max=precio_max,
            en_stock=en_stock,
            orden=orden,
            incluir_eliminados=incluir_eliminados,
        )


@router.get("/{producto_id}", response_model=ProductoRead)
def get_producto(producto_id: int, uow: ProductoUnitOfWork = Depends(get_producto_uow)):
    with uow:
        return ProductoService(uow).get_by_id(producto_id)


@router.put(
    "/{producto_id}",
    response_model=ProductoRead,
    dependencies=[Depends(require_role(["ADMIN", "STOCK"]))],
)
def update_producto(producto_id: int, data: ProductoUpdate, uow: ProductoUnitOfWork = Depends(get_producto_uow)):
    with uow:
        return ProductoService(uow).update(producto_id, data)


@router.delete(
    "/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(["ADMIN"]))],
)
def delete_producto(producto_id: int, uow: ProductoUnitOfWork = Depends(get_producto_uow)):
    with uow:
        ProductoService(uow).soft_delete(producto_id)


@router.patch(
    "/{producto_id}/restaurar",
    response_model=ProductoRead,
    summary="Restaurar producto eliminado",
    dependencies=[Depends(require_role(["ADMIN"]))],
)
def restore_producto(producto_id: int, uow: ProductoUnitOfWork = Depends(get_producto_uow)):
    with uow:
        return ProductoService(uow).restore(producto_id)


# ── Disponibilidad ──────────────────────────────────────────────────────────

@router.patch(
    "/{producto_id}/disponibilidad",
    response_model=ProductoRead,
    dependencies=[Depends(require_role(["ADMIN", "STOCK"]))],
    summary="Cambiar disponibilidad del producto",
)
def toggle_disponibilidad(
    producto_id: int,
    data: DisponibilidadUpdate,
    uow: ProductoUnitOfWork = Depends(get_producto_uow),
):
    with uow:
        return ProductoService(uow).toggle_disponibilidad(producto_id, data)


# ── Imágenes ────────────────────────────────────────────────────────────────

@router.patch(
    "/{producto_id}/imagenes",
    response_model=ProductoRead,
    dependencies=[Depends(require_role(["ADMIN"]))],
    summary="Actualizar lista de imágenes del producto",
)
def update_imagenes(
    producto_id: int,
    data: ImagenesProductoUpdate,
    uow: ProductoUnitOfWork = Depends(get_producto_uow),
):
    with uow:
        return ProductoService(uow).update_imagenes(producto_id, data)


# ── Ingredientes del producto ───────────────────────────────────────────────

@router.get(
    "/{producto_id}/ingredientes",
    response_model=list[ProductoIngredienteRead],
    summary="Listar ingredientes del producto",
)
def list_ingredientes(
    producto_id: int,
    uow: ProductoUnitOfWork = Depends(get_producto_uow),
):
    with uow:
        return ProductoService(uow).get_ingredientes(producto_id)


@router.post(
    "/{producto_id}/ingredientes",
    response_model=list[ProductoIngredienteRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(["ADMIN"]))],
    summary="Asociar ingrediente al producto",
)
def add_ingrediente(
    producto_id: int,
    data: ProductoIngredienteCreate,
    uow: ProductoUnitOfWork = Depends(get_producto_uow),
):
    with uow:
        return ProductoService(uow).add_ingrediente(producto_id, data)
