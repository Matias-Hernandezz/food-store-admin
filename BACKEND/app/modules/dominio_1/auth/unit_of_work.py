from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.dominio_1.auth.repository import RefreshTokenRepository
from app.modules.dominio_1.usuarios.repository import UsuarioRepository, RolRepository, UsuarioRolRepository


class AuthUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.usuarios = UsuarioRepository(session)
        self.refresh_tokens = RefreshTokenRepository(session)
        self.roles = RolRepository(session)
        self.usuario_roles = UsuarioRolRepository(session)
