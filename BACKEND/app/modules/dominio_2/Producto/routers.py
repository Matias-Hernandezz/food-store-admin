from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session
from app.core.db import get_session
from app.modules.dominio_2.Producto.services import ProductoService
from app.modules.dominio_2.Producto.schemas import ProductoCreate, ProductoUpdate, ProductoRead, ProductoList

router = APIRouter(prefix="/productos", tags=["Productos"])

def get_producto_service(session: Session = Depends(get_session)) -> ProductoService:
    return ProductoService(session)

@router.post("/", response_model=ProductoRead, status_code=status.HTTP_201_CREATED)
def create_producto(data: ProductoCreate, svc: ProductoService = Depends(get_producto_service)):
    return svc.create(data)

@router.get("/", response_model=ProductoList)
def list_productos(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    svc: ProductoService = Depends(get_producto_service)
):
    return svc.get_all(offset, limit)

@router.get("/{producto_id}", response_model=ProductoRead)
def get_producto(producto_id: int, svc: ProductoService = Depends(get_producto_service)):
    return svc.get_by_id(producto_id)

@router.patch("/{producto_id}", response_model=ProductoRead)
def update_producto(producto_id: int, data: ProductoUpdate, svc: ProductoService = Depends(get_producto_service)):
    return svc.update(producto_id, data)

@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto(producto_id: int, svc: ProductoService = Depends(get_producto_service)):
    svc.soft_delete(producto_id)