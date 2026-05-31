from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, select

from app.core.repository import BaseRepository
from app.modules.dominio_1.Usuarios.models import Usuario, Rol, UsuarioRol, DireccionEntrega, RefreshToken


class UsuarioRepository(BaseRepository[Usuario]):

    def __init__(self, session: Session):
        super().__init__(session, Usuario)

    def get_by_email(self, email: str) -> Optional[Usuario]:
        return self.session.exec(
            select(Usuario).where(
                Usuario.email == email,
                Usuario.deleted_at.is_(None),   
            )
        ).first()

    def get_all_active(self, offset: int = 0, limit: int = 20) -> list[Usuario]:
        return list(
            self.session.exec(
                select(Usuario)
                .where(Usuario.deleted_at.is_(None))  
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def soft_delete(self, usuario: Usuario) -> Usuario:
        usuario.deleted_at = datetime.now(timezone.utc)
        self.session.add(usuario)
        self.session.flush()
        return usuario


class RolRepository(BaseRepository[Rol]):

    def __init__(self, session: Session):
        super().__init__(session,Rol )

    def get_by_codigo(self, codigo: str) -> Optional[Rol]:
        return self.session.get(Rol, codigo)

    def get_all(self) -> list[Rol]:
        return list(self.session.exec(select(Rol)).all())

class UsuarioRolRepository(BaseRepository[UsuarioRol]):

    def __init__(self, session: Session):
        super().__init__(session,UsuarioRol)

    def get_roles_de_usuario(self, usuario_id: int) -> list[str]:
        rows = self.session.exec(
            select(UsuarioRol).where(UsuarioRol.usuario_id == usuario_id)
        ).all()
        return [r.rol_codigo for r in rows]

    def existe(self, usuario_id: int, rol_codigo: str) -> bool:
        return self.session.exec(
            select(UsuarioRol).where(
                UsuarioRol.usuario_id == usuario_id,
                UsuarioRol.rol_codigo == rol_codigo,
            )
        ).first() is not None

    def eliminar(self, usuario_id: int, rol_codigo: str) -> None:
        row = self.session.exec(
            select(UsuarioRol).where(
                UsuarioRol.usuario_id == usuario_id,
                UsuarioRol.rol_codigo == rol_codigo,
            )
        ).first()
        if row:
            self.session.delete(row)
            self.session.flush()
    
def delete_by_user_and_rol(self, usuario_id: int, rol_codigo: str) -> None:
   
    statement = select(UsuarioRol).where(
        UsuarioRol.usuario_id == usuario_id,
        UsuarioRol.rol_codigo == rol_codigo
    )
    row = self.session.exec(statement).first()
    if row:
        self.session.delete(row)
        self.session.flush()

class DireccionRepository(BaseRepository[DireccionEntrega]):

    def __init__(self, session: Session):
        super().__init__(session,DireccionEntrega)

    def get_activas_por_usuario(self, usuario_id: int) -> list[DireccionEntrega]:
        return list(
            self.session.exec(
                select(DireccionEntrega).where(
                    DireccionEntrega.usuario_id == usuario_id,
                    DireccionEntrega.deleted_at.is_(None),  
                )
            ).all()
        )

    def get_principal(self, usuario_id: int) -> Optional[DireccionEntrega]:
        return self.session.exec(
            select(DireccionEntrega).where(
                DireccionEntrega.usuario_id == usuario_id,
                DireccionEntrega.es_principal == True,  
                DireccionEntrega.deleted_at.is_(None),  
            )
        ).first()

    def soft_delete(self, direccion: DireccionEntrega) -> None:
        direccion.deleted_at = datetime.now(timezone.utc)
        self.session.add(direccion)
        self.session.flush()

class RefreshTokenRepository(BaseRepository[RefreshToken]):

    def __init__(self, session: Session):
        super().__init__(session,RefreshToken)

    def get_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        return self.session.exec(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        ).first()

    def revocar(self, token: RefreshToken) -> None:
        token.revoked_at = datetime.now(timezone.utc)
        self.session.add(token)
        self.session.flush()