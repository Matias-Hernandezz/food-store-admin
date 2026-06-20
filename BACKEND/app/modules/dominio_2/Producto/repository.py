from typing import Optional

from sqlmodel import Session, select, func

from app.core.repository import BaseRepository
from app.modules.dominio_2.Producto.models import Producto
from app.modules.dominio_2.Producto.models_shared import ProductoIngrediente
from app.modules.dominio_2.Ingrediente.models import Ingrediente


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
            select(Producto).where(Producto.nombre == nombre)
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

    def get_filtered(
        self,
        offset: int = 0,
        limit: int = 20,
        categoria_id: Optional[int] = None,
        disponible: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> list[Producto]:
        stmt = select(Producto).where(Producto.deleted_at.is_(None))

        if disponible is not None:
            stmt = stmt.where(Producto.disponible == disponible)

        if search:
            stmt = stmt.where(Producto.nombre.ilike(f"%{search}%"))

        if categoria_id is not None:
            from app.modules.dominio_2.Producto.models_shared import ProductoCategoria
            stmt = stmt.join(
                ProductoCategoria,
                ProductoCategoria.producto_id == Producto.id,
            ).where(ProductoCategoria.categoria_id == categoria_id)

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
    ) -> int:
        stmt = select(func.count()).select_from(Producto).where(
            Producto.deleted_at.is_(None)
        )

        if disponible is not None:
            stmt = stmt.where(Producto.disponible == disponible)

        if search:
            stmt = stmt.where(Producto.nombre.ilike(f"%{search}%"))

        if categoria_id is not None:
            from app.modules.dominio_2.Producto.models_shared import ProductoCategoria
            stmt = stmt.join(
                ProductoCategoria,
                ProductoCategoria.producto_id == Producto.id,
            ).where(ProductoCategoria.categoria_id == categoria_id)

        return self.session.scalar(stmt)
