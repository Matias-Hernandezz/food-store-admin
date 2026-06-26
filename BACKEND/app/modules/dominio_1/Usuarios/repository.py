from sqlmodel import Session, select, func
from app.core.repository import BaseRepository
from app.modules.dominio_1.usuarios.models import Usuario, Rol, UsuarioRol


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Usuario)

    def get_by_id_with_roles(self, usuario_id: int) -> Usuario | None:
        stmt = (
            select(Usuario)
            .where(Usuario.id == usuario_id)
            .where(Usuario.deleted_at.is_(None))
        )
        return self.session.exec(stmt).first()

    def get_by_email(self, email: str) -> Usuario | None:
        """Busca por email SIN filtrar deleted_at."""
        return self.session.exec(
            select(Usuario).where(Usuario.email == email)
        ).first()

    def get_all_active(
        self, offset: int = 0, limit: int = 100, search: str | None = None
    ) -> list[Usuario]:
        stmt = select(Usuario).where(Usuario.deleted_at.is_(None))
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                (Usuario.nombre.ilike(pattern))
                | (Usuario.apellido.ilike(pattern))
                | (Usuario.email.ilike(pattern))
            )
        return list(
            self.session.exec(stmt.offset(offset).limit(limit)).all()
        )

    def count_active(self, search: str | None = None) -> int:
        stmt = (
            select(func.count())
            .select_from(Usuario)
            .where(Usuario.deleted_at.is_(None))
        )
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                (Usuario.nombre.ilike(pattern))
                | (Usuario.apellido.ilike(pattern))
                | (Usuario.email.ilike(pattern))
            )
        return self.session.scalar(stmt)


class RolRepository(BaseRepository[Rol]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Rol)

    def get_by_codigo(self, codigo: str) -> Rol | None:
        return self.session.exec(
            select(Rol).where(Rol.codigo == codigo)
        ).first()


class UsuarioRolRepository(BaseRepository[UsuarioRol]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, UsuarioRol)

    def get_roles_de_usuario(self, usuario_id: int) -> list[str]:
        results = self.session.exec(
            select(UsuarioRol.rol_codigo).where(
                UsuarioRol.usuario_id == usuario_id
            )
        ).all()
        return list(results)

    def existe(self, usuario_id: int, rol_codigo: str) -> bool:
        return self.session.exec(
            select(UsuarioRol).where(
                UsuarioRol.usuario_id == usuario_id,
                UsuarioRol.rol_codigo == rol_codigo,
            )
        ).first() is not None

    def eliminar(self, usuario_id: int, rol_codigo: str) -> None:
        registro = self.session.exec(
            select(UsuarioRol).where(
                UsuarioRol.usuario_id == usuario_id,
                UsuarioRol.rol_codigo == rol_codigo,
            )
        ).first()
        if registro:
            self.session.delete(registro)
            self.session.flush()
