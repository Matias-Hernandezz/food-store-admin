from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.dominio_1.direcciones.repository import DireccionRepository
from app.modules.dominio_1.usuarios.repository import UsuarioRepository


class DireccionUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.direcciones = DireccionRepository(session)
        self.usuarios = UsuarioRepository(session)
