import math
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status

from app.modules.dominio_2.productos.models import Producto
from app.modules.dominio_2.productos.models_shared import ProductoIngrediente
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
from app.modules.dominio_2.productos.unit_of_work import ProductoUnitOfWork
from app.modules.dominio_2.unidad_medida.schemas import UnidadMedidaRead


class ProductoService:
    """Lógica de negocio del módulo Productos.

    Recibe un ProductoUnitOfWork del router (ya abierto via context manager).
    El commit/rollback lo gestiona el UoW, NUNCA el service.
    """

    def __init__(self, uow: ProductoUnitOfWork) -> None:
        self.uow = uow

    def _get_or_404(self, producto_id: int) -> Producto:
        producto = self.uow.productos.get_by_id(producto_id)
        if not producto or producto.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id={producto_id} no encontrado",
            )
        return producto

    def _to_read(self, producto: Producto) -> ProductoRead:
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
            unidad_venta_id=producto.unidad_venta_id,
            cantidad_venta=producto.cantidad_venta,
            unidad_venta=UnidadMedidaRead.model_validate(producto.unidad_venta) if producto.unidad_venta else None,
            categoria_ids=[c.id for c in producto.categorias],
            ingrediente_ids=[i.id for i in producto.ingredientes],
        )

    # ── CRUD ─────────────────────────────────────────────────────────────

    def create(self, data: ProductoCreate) -> ProductoRead:
        """Crea un producto con categorías asociadas. Valida unicidad de nombre."""
        if self.uow.productos.get_by_nombre(data.nombre):
            raise HTTPException(status_code=409, detail="El nombre del producto ya existe")
        if not data.categoria_ids:
            raise HTTPException(status_code=400, detail="El producto debe tener al menos una categoría")

        producto = Producto.model_validate(data)
        for cat_id in data.categoria_ids:
            cat = self.uow.categorias.get_by_id(cat_id)
            if not cat or cat.deleted_at:
                raise HTTPException(status_code=404, detail=f"Categoría {cat_id} no válida")
            producto.categorias.append(cat)

        if data.ingrediente_ids:
            for ing_id in data.ingrediente_ids:
                ing = self.uow.ingredientes.get_by_id(ing_id)
                if not ing:
                    raise HTTPException(status_code=404, detail=f"Ingrediente {ing_id} no válido")
                producto.ingredientes.append(ing)

        self.uow.productos.add(producto)
        return self._to_read(producto)

    def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        categoria_id: Optional[int] = None,
        disponible: Optional[bool] = None,
        search: Optional[str] = None,
        precio_min: Optional[Decimal] = None,
        precio_max: Optional[Decimal] = None,
        en_stock: bool = False,
        orden: Optional[str] = None,
        incluir_eliminados: bool = False,
    ) -> ProductoList:
        productos = self.uow.productos.get_filtered(
            offset=offset, limit=limit,
            categoria_id=categoria_id,
            disponible=disponible,
            search=search,
            precio_min=precio_min,
            precio_max=precio_max,
            en_stock=en_stock,
            orden=orden,
            incluir_eliminados=incluir_eliminados,
        )
        total = self.uow.productos.count_filtered(
            categoria_id=categoria_id,
            disponible=disponible,
            search=search,
            precio_min=precio_min,
            precio_max=precio_max,
            en_stock=en_stock,
            incluir_eliminados=incluir_eliminados,
        )
        return ProductoList(
            data=[self._to_read(p) for p in productos],
            total=total,
            page=(offset // limit) + 1 if limit else 1,
            size=limit,
            pages=max(1, math.ceil(total / limit)) if limit else 1,
        )

    def get_by_id(self, producto_id: int) -> ProductoRead:
        producto = self._get_or_404(producto_id)
        return self._to_read(producto)

    def update(self, producto_id: int, data: ProductoUpdate) -> ProductoRead:
        producto = self._get_or_404(producto_id)

        if data.nombre and data.nombre != producto.nombre:
            if self.uow.productos.get_by_nombre(data.nombre):
                raise HTTPException(status_code=409, detail="Nombre ya en uso")

        patch = data.model_dump(exclude_unset=True)

        if 'categoria_ids' in patch:
            if not patch['categoria_ids']:
                raise HTTPException(status_code=400, detail="El producto debe tener al menos una categoría")
            producto.categorias.clear()
            for cat_id in patch['categoria_ids']:
                cat = self.uow.categorias.get_by_id(cat_id)
                if not cat or cat.deleted_at:
                    raise HTTPException(status_code=404, detail=f"Categoría {cat_id} no válida")
                producto.categorias.append(cat)
            del patch['categoria_ids']

        if 'ingrediente_ids' in patch:
            producto.ingredientes.clear()
            if patch['ingrediente_ids']:
                for ing_id in patch['ingrediente_ids']:
                    ing = self.uow.ingredientes.get_by_id(ing_id)
                    if not ing:
                        raise HTTPException(status_code=404, detail=f"Ingrediente {ing_id} no válido")
                    producto.ingredientes.append(ing)
            del patch['ingrediente_ids']

        for field, value in patch.items():
            setattr(producto, field, value)

        self.uow.productos.add(producto)
        return self._to_read(producto)

    def soft_delete(self, producto_id: int) -> None:
        producto = self._get_or_404(producto_id)
        producto.deleted_at = datetime.now(timezone.utc)
        self.uow.productos.add(producto)

    def restore(self, producto_id: int) -> ProductoRead:
        producto = self.uow.productos.get_by_id(producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id={producto_id} no encontrado",
            )
        if producto.deleted_at is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El producto no está eliminado",
            )
        # Verificar que no exista otro producto activo con el mismo nombre
        existente = self.uow.productos.get_by_nombre(producto.nombre)
        if existente and existente.id != producto_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"No se puede restaurar: ya existe un producto activo con el nombre '{producto.nombre}'",
            )
        self.uow.productos.restore(producto)
        return self._to_read(producto)

    # ── Disponibilidad ───────────────────────────────────────────────────

    def toggle_disponibilidad(self, producto_id: int, data: DisponibilidadUpdate) -> ProductoRead:
        producto = self._get_or_404(producto_id)
        producto.disponible = data.disponible
        self.uow.productos.add(producto)
        return self._to_read(producto)

    # ── Imágenes ─────────────────────────────────────────────────────────

    def update_imagenes(self, producto_id: int, data: ImagenesProductoUpdate) -> ProductoRead:
        producto = self._get_or_404(producto_id)
        producto.imagenes_url = data.imagenes_url
        self.uow.productos.add(producto)
        return self._to_read(producto)

    # ── Ingredientes del producto ────────────────────────────────────────

    def get_ingredientes(self, producto_id: int) -> list[ProductoIngredienteRead]:
        self._get_or_404(producto_id)
        rows = self.uow.productos.get_ingredientes_producto(producto_id)

        result = []
        for pi, ing in rows:
            unidad = self.uow.unidad_medida.get_by_id(pi.unidad_medida_id)
            result.append(ProductoIngredienteRead(
                ingrediente_id=ing.id,
                nombre=ing.nombre,
                cantidad=pi.cantidad,
                unidad_simbolo=unidad.simbolo if unidad else "?",
                es_removible=pi.es_removible,
                es_alergeno=ing.es_alergeno,
            ))
        return result

    def add_ingrediente(self, producto_id: int, data: ProductoIngredienteCreate) -> list[ProductoIngredienteRead]:
        producto = self._get_or_404(producto_id)

        ing = self.uow.ingredientes.get_by_id(data.ingrediente_id)
        if not ing:
            raise HTTPException(status_code=404, detail=f"Ingrediente {data.ingrediente_id} no encontrado")

        # Verificar que no esté ya asociado
        existing = self.uow.productos.get_producto_ingrediente(producto_id, data.ingrediente_id)
        if existing:
            raise HTTPException(status_code=409, detail="El ingrediente ya está asociado a este producto")

        pi = ProductoIngrediente(
            producto_id=producto_id,
            ingrediente_id=data.ingrediente_id,
            cantidad=data.cantidad,
            unidad_medida_id=data.unidad_medida_id,
            es_removible=data.es_removible,
        )
        self.uow.productos.add_producto_ingrediente(pi)

        # Recargar lista completa
        return self.get_ingredientes(producto_id)
