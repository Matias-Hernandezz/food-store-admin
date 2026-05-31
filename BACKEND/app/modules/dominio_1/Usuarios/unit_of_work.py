from app.core.unit_of_work import UnitOfWork
from app.modules.dominio_1.Usuarios.repository import UsuarioRepository, RolRepository, UsuarioRolRepository, DireccionRepository, RefreshTokenRepository

class UsuarioUnitOfWork(UnitOfWork):
    def __enter__(self):
        self.usuarios = UsuarioRepository(self._session)
        self.roles = RolRepository(self._session)
        self.usuario_roles = UsuarioRolRepository(self._session)
        self.direcciones = DireccionRepository(self._session)
        self.refresh_tokens = RefreshTokenRepository(self._session)
        return self
