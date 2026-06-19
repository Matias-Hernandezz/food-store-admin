from typing import Optional

from sqlmodel import Session, select, func

from app.core.repository import BaseRepository
from app.modules.dominio_2.Producto.models import Producto


class ProductoRepository(BaseRepository[Producto]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Producto)

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
