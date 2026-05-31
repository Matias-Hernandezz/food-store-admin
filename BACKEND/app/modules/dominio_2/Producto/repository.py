from sqlmodel import Session, select
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
        return len(self.session.exec(
            select(Producto).where(Producto.deleted_at.is_(None))
        ).all())