from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.dominio_2.Ingrediente.models import Ingrediente

class IngredienteRepository(BaseRepository[Ingrediente]):
    
    def __init__(self, session: Session) -> None:
        
        super().__init__(session, Ingrediente)

    def get_by_nombre(self, nombre: str) -> Ingrediente | None:
       
        return self.session.exec(
            select(Ingrediente).where(Ingrediente.nombre == nombre)
        ).first()

    def get_active(self, offset: int = 0, limit: int = 20) -> list[Ingrediente]:
    
        return list(
            self.session.exec(
                select(Ingrediente)
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def count_active(self) -> int:
     
        return len(
            self.session.exec(
                select(Ingrediente)
            ).all()
        )