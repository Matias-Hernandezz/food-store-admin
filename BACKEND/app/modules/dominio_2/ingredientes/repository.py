from datetime import datetime, timezone
from typing import Sequence
from sqlmodel import Session, select, func
from app.core.repository import BaseRepository
from app.modules.dominio_2.ingredientes.models import Ingrediente

class IngredienteRepository(BaseRepository[Ingrediente]):
    
    def __init__(self, session: Session) -> None:
        super().__init__(session, Ingrediente)

    def get_by_nombre(self, nombre: str) -> Ingrediente | None:
        return self.session.exec(
            select(Ingrediente).where(
                Ingrediente.nombre == nombre,
                Ingrediente.deleted_at.is_(None),
            )
        ).first()

    def get_active(self, offset: int = 0, limit: int = 20) -> list[Ingrediente]:
        return list(
            self.session.exec(
                select(Ingrediente)
                .where(Ingrediente.deleted_at.is_(None))
                .order_by(Ingrediente.created_at.desc())
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def get_all(self, offset: int = 0, limit: int = 100) -> Sequence[Ingrediente]:
        return self.session.exec(
            select(Ingrediente)
            .order_by(Ingrediente.created_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()

    def count_active(self) -> int:
        return self.session.scalar(
            select(func.count()).select_from(Ingrediente).where(
                Ingrediente.deleted_at.is_(None)
            )
        )

    def soft_delete(self, ingrediente: Ingrediente) -> None:
        ingrediente.deleted_at = datetime.now(timezone.utc)
        self.session.add(ingrediente)
        self.session.flush()
