from typing import Optional
from decimal import Decimal

from sqlalchemy import or_
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import Session, select, func

from app.core.repository import BaseRepository
from app.modules.dominio_2.productos.models import Producto
from app.modules.dominio_2.productos.models_shared import ProductoIngrediente
from app.modules.dominio_2.ingredientes.models import Ingrediente
from app.modules.dominio_2.categorias.models import Categoria


class ProductoRepository(BaseRepository[Producto]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Producto)

    # ── ProductoIngrediente ───────────────────────────────────────────────

    def get_ingredientes_producto(self, producto_id: int) -> list[tuple[ProductoIngrediente, Ingrediente]]:
        """Devuelve (ProductoIngrediente, Ingrediente) para un producto."""
        return list(
            self.session.exec(
                select(ProductoIngrediente, Ingrediente)
                .join(Ingrediente, ProductoIngrediente.ingrediente_id == Ingrediente.id)
                .where(ProductoIngrediente.producto_id == producto_id)
            ).all()
        )

    def get_producto_ingrediente(self, producto_id: int, ingrediente_id: int) -> ProductoIngrediente | None:
        """Verifica si un ingrediente ya está asociado al producto."""
        return self.session.exec(
            select(ProductoIngrediente).where(
                ProductoIngrediente.producto_id == producto_id,
                ProductoIngrediente.ingrediente_id == ingrediente_id,
            )
        ).first()

    def add_producto_ingrediente(self, pi: ProductoIngrediente) -> ProductoIngrediente:
        """Agrega una relación ProductoIngrediente."""
        self.session.add(pi)
        self.session.flush()
        return pi

    def get_by_nombre(self, nombre: str) -> Producto | None:
        return self.session.exec(
            select(Producto).where(
                Producto.nombre == nombre,
                Producto.deleted_at.is_(None),
            )
        ).first()

    def get_active(self, offset: int = 0, limit: int = 20) -> list[Producto]:
        return list(
            self.session.exec(
                select(Producto)
                .where(Producto.deleted_at.is_(None))
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def count_active(self) -> int:
        return self.session.scalar(
            select(func.count()).select_from(Producto).where(
                Producto.deleted_at.is_(None)
            )
        )

    # ── Filtros ──────────────────────────────────────────────────────────

    def _get_category_tree_ids(self, categoria_id: int) -> list[int]:
        """Devuelve categoria_id + todos sus descendientes (recursivo)."""
        ids = [categoria_id]
        hijos = self.session.exec(
            select(Categoria.id).where(
                Categoria.parent_id == categoria_id,
                Categoria.deleted_at.is_(None),
            )
        ).all()
        for hijo_id in hijos:
            ids.extend(self._get_category_tree_ids(hijo_id))
        return ids

    def get_filtered(
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
    ) -> list[Producto]:
        stmt = select(Producto).options(
            joinedload(Producto.unidad_venta),
            selectinload(Producto.categorias),
            selectinload(Producto.ingredientes),
        )
        if not incluir_eliminados:
            stmt = stmt.where(Producto.deleted_at.is_(None))

        if disponible is not None:
            stmt = stmt.where(Producto.disponible == disponible)

        if search:
            stmt = stmt.where(
                or_(
                    Producto.nombre.ilike(f"%{search}%"),
                    Producto.descripcion.ilike(f"%{search}%"),
                )
            )

        if precio_min is not None:
            stmt = stmt.where(Producto.precio_base >= precio_min)
        if precio_max is not None:
            stmt = stmt.where(Producto.precio_base <= precio_max)

        if en_stock:
            stmt = stmt.where(Producto.stock_cantidad > 0)

        if categoria_id is not None:
            from app.modules.dominio_2.productos.models_shared import ProductoCategoria
            cat_ids = self._get_category_tree_ids(categoria_id)
            # Subquery en vez de JOIN — evita duplicar filas con joinedload
            subq = select(ProductoCategoria.producto_id).where(
                ProductoCategoria.categoria_id.in_(cat_ids)
            ).distinct()
            stmt = stmt.where(Producto.id.in_(subq))

        # Ordenamiento
        if orden == "precio_asc":
            stmt = stmt.order_by(Producto.precio_base.asc())
        elif orden == "precio_desc":
            stmt = stmt.order_by(Producto.precio_base.desc())
        elif orden == "nombre":
            stmt = stmt.order_by(Producto.nombre.asc())
        else:
            stmt = stmt.order_by(Producto.created_at.desc())

        return list(
            self.session.exec(
                stmt.offset(offset).limit(limit)
            ).all()
        )

    def count_filtered(
        self,
        categoria_id: Optional[int] = None,
        disponible: Optional[bool] = None,
        search: Optional[str] = None,
        precio_min: Optional[Decimal] = None,
        precio_max: Optional[Decimal] = None,
        en_stock: bool = False,
        incluir_eliminados: bool = False,
    ) -> int:
        stmt = select(func.count()).select_from(Producto)
        if not incluir_eliminados:
            stmt = stmt.where(Producto.deleted_at.is_(None))

        if disponible is not None:
            stmt = stmt.where(Producto.disponible == disponible)

        if search:
            stmt = stmt.where(
                or_(
                    Producto.nombre.ilike(f"%{search}%"),
                    Producto.descripcion.ilike(f"%{search}%"),
                )
            )

        if precio_min is not None:
            stmt = stmt.where(Producto.precio_base >= precio_min)
        if precio_max is not None:
            stmt = stmt.where(Producto.precio_base <= precio_max)

        if en_stock:
            stmt = stmt.where(Producto.stock_cantidad > 0)

        if categoria_id is not None:
            from app.modules.dominio_2.productos.models_shared import ProductoCategoria
            cat_ids = self._get_category_tree_ids(categoria_id)
            subq = select(ProductoCategoria.producto_id).where(
                ProductoCategoria.categoria_id.in_(cat_ids)
            ).distinct()
            stmt = stmt.where(Producto.id.in_(subq))

        return self.session.scalar(stmt)
