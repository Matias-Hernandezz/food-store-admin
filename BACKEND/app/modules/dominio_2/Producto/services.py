from fastapi import HTTPException, status
from sqlmodel import Session
from datetime import datetime, timezone
from app.modules.dominio_2.Producto.unit_of_work import ProductoUnitOfWork
from app.modules.dominio_2.Producto.schemas import ProductoCreate, ProductoUpdate, ProductoRead, ProductoList
from app.modules.dominio_2.Producto.models import Producto

class ProductoService:
    def __init__(self, session: Session) -> None:
        self._session = session


    def _get_or_404(self, uow: ProductoUnitOfWork, producto_id: int) -> Producto:
        producto = uow.productos.get_by_id(producto_id)
        if not producto or producto.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id={producto_id} no encontrado",
            )
        return producto

    def _to_read(self, producto: Producto) -> ProductoRead:
        categorias = list(producto.categorias)
        ingredientes = list(producto.ingredientes)
        return ProductoRead(
            id=producto.id,
            nombre=producto.nombre,
            descripcion=producto.descripcion,
            precio_base=producto.precio_base,
            imagenes_url=producto.imagenes_url,
            stock_cantidad=producto.stock_cantidad,
            disponible=producto.disponible,
            created_at=producto.created_at,
            updated_at=producto.updated_at,
            deleted_at=producto.deleted_at,
            categoria_ids=[c.id for c in producto.categorias],
            ingrediente_ids=[i.id for i in producto.ingredientes],
        )

   
    def create(self, data: ProductoCreate) -> ProductoRead:
        with ProductoUnitOfWork(self._session) as uow:
            if uow.productos.get_by_nombre(data.nombre):
                raise HTTPException(status_code=409, detail="El nombre del producto ya existe")

            if not data.categoria_ids:
                raise HTTPException(status_code=400, detail="El producto debe tener al menos una categoría")
            producto = Producto.model_validate(data)
            
            for cat_id in data.categoria_ids:
                cat = uow.categorias.get_by_id(cat_id)
                if not cat or cat.deleted_at:
                    raise HTTPException(status_code=404, detail=f"Categoría {cat_id} no válida")
                producto.categorias.append(cat)
            
            if data.ingrediente_ids:
                for ing_id in data.ingrediente_ids:
                    ing = uow.ingredientes.get_by_id(ing_id)
                    if not ing:
                        raise HTTPException(status_code=404, detail=f"Ingrediente {ing_id} no válido")
                    producto.ingredientes.append(ing)
            
            uow.productos.add(producto)
            return self._to_read(producto)

    def get_all(self, offset: int = 0, limit: int = 20) -> ProductoList:
        with ProductoUnitOfWork(self._session) as uow:
            productos = uow.productos.get_active(offset=offset, limit=limit)
            total = uow.productos.count_active()
            return ProductoList(
                data=[self._to_read(p) for p in productos],
                total=total
            )

    def get_by_id(self, producto_id: int) -> ProductoRead:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            return self._to_read(producto)

    def update(self, producto_id: int, data: ProductoUpdate) -> ProductoRead:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)

            if data.nombre and data.nombre != producto.nombre:
                if uow.productos.get_by_nombre(data.nombre):
                    raise HTTPException(status_code=409, detail="Nombre ya en uso")

            patch = data.model_dump(exclude_unset=True)
            
            if 'categoria_ids' in patch:
                if not patch['categoria_ids']:
                    raise HTTPException(status_code=400, detail="El producto debe tener al menos una categoría")
                producto.categorias.clear()
                for cat_id in patch['categoria_ids']:
                    cat = uow.categorias.get_by_id(cat_id)
                    if not cat or cat.deleted_at:
                        raise HTTPException(status_code=404, detail=f"Categoría {cat_id} no válida")
                    producto.categorias.append(cat)
                del patch['categoria_ids']
            
            if 'ingrediente_ids' in patch:
                producto.ingredientes.clear()
                if patch['ingrediente_ids']:
                    for ing_id in patch['ingrediente_ids']:
                        ing = uow.ingredientes.get_by_id(ing_id)
                        if not ing:
                            raise HTTPException(status_code=404, detail=f"Ingrediente {ing_id} no válido")
                        producto.ingredientes.append(ing)
                del patch['ingrediente_ids']

            for field, value in patch.items():
                setattr(producto, field, value)

            uow.productos.add(producto)
            return self._to_read(producto)

    def soft_delete(self, producto_id: int) -> None:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            producto.deleted_at = datetime.now(timezone.utc)
            uow.productos.add(producto)