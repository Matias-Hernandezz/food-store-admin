from datetime import datetime, timezone
from fastapi import HTTPException, status

from app.modules.dominio_1.usuarios.unit_of_work import UsuarioUnitOfWork
from app.modules.dominio_1.usuarios.models import Usuario, UsuarioRol
from app.modules.dominio_1.usuarios.schemas import UsuarioRead, UsuarioUpdate


class UsuarioService:
    def __init__(self, uow: UsuarioUnitOfWork) -> None:
        self.uow = uow

    def _get_or_404(self, usuario_id: int) -> Usuario:
        usuario = self.uow.usuarios.get_by_id(usuario_id)
        if not usuario or usuario.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con id={usuario_id} no encontrado",
            )
        return usuario

    def _get_roles(self, usuario_id: int) -> list[str]:
        return self.uow.usuario_roles.get_roles_de_usuario(usuario_id)

    def _to_read(self, usuario: Usuario) -> UsuarioRead:
        roles = self._get_roles(usuario.id)
        return UsuarioRead(
            id=usuario.id,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            email=usuario.email,
            celular=usuario.celular,
            roles=roles,
            created_at=usuario.created_at,
            deleted_at=usuario.deleted_at,
        )

    def listar_usuarios(
        self, search: str | None = None, offset: int = 0, limit: int = 100
    ) -> list[UsuarioRead]:
        usuarios = self.uow.usuarios.get_all_active(
            offset=offset, limit=limit, search=search
        )
        return [self._to_read(u) for u in usuarios]

    def actualizar_usuario(self, usuario_id: int, data: UsuarioUpdate) -> UsuarioRead:
        usuario = self._get_or_404(usuario_id)
        patch = data.model_dump(exclude_unset=True)
        for field, value in patch.items():
            setattr(usuario, field, value)
        self.uow.usuarios.add(usuario)
        return self._to_read(usuario)

    def soft_delete_usuario(self, usuario_id: int) -> None:
        usuario = self._get_or_404(usuario_id)
        usuario.deleted_at = datetime.now(timezone.utc)
        self.uow.usuarios.add(usuario)

    def asignar_rol(self, usuario_id: int, rol_codigo: str) -> UsuarioRead:
        usuario = self._get_or_404(usuario_id)
        rol = self.uow.roles.get_by_codigo(rol_codigo)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rol '{rol_codigo}' no encontrado",
            )
        if not self.uow.usuario_roles.existe(usuario_id, rol_codigo):
            ur = UsuarioRol(usuario_id=usuario_id, rol_codigo=rol_codigo)
            self.uow.usuario_roles.add(ur)
        return self._to_read(usuario)

    def quitar_rol(self, usuario_id: int, rol_codigo: str) -> UsuarioRead:
        self._get_or_404(usuario_id)
        self.uow.usuario_roles.eliminar(usuario_id, rol_codigo)
        usuario = self._get_or_404(usuario_id)
        return self._to_read(usuario)
