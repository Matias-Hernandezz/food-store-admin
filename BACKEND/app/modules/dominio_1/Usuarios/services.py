from app.modules.dominio_1.Usuarios.models import DireccionEntrega
from app.modules.dominio_1.Usuarios.schemas import DireccionRead, DireccionCreate
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from app.core.security import (
    hash_password, verify_password,
    create_access_token,
    generate_refresh_token, hash_refresh_token,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from app.modules.dominio_1.Usuarios.models import Usuario, RefreshToken, UsuarioRol
from app.modules.dominio_1.Usuarios.schemas import UsuarioCreate, UsuarioRead
from app.modules.dominio_1.Usuarios.unit_of_work import UsuarioUnitOfWork

class AuthService:

    def __init__(self, uow: UsuarioUnitOfWork):
        self.uow = uow

    #register
    def register(self, data: UsuarioCreate) -> UsuarioRead:
        if self.uow.usuarios.get_by_email(str(data.email)):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya está registrado",  
            )

        usuario = Usuario(
            nombre=data.nombre,
            apellido=data.apellido,
            email=str(data.email),
            celular=data.celular,
            password_hash=hash_password(data.password),
        )
        usuario = self.uow.usuarios.add(usuario)

        self.uow.usuario_roles.add(
            UsuarioRol(usuario_id=usuario.id, rol_codigo="CLIENT") 
        )

        return self._to_read(usuario)

    def login(self, email: str, password: str) -> tuple[str, str]:
        usuario = self.uow.usuarios.get_by_email(email)

        if not usuario or not verify_password(password, usuario.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
            )

        if usuario.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cuenta eliminada",
            )

        roles = self.uow.usuario_roles.get_roles_de_usuario(usuario.id)
        access_token = create_access_token(usuario.id, roles)

        raw_refresh = generate_refresh_token()
        self.uow.refresh_tokens.add(
            RefreshToken(
                usuario_id=usuario.id,
                token_hash=hash_refresh_token(raw_refresh),
                expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            )
        )
        return access_token, raw_refresh

    def refresh(self, raw_refresh: str) -> str:
        token = self.uow.refresh_tokens.get_by_hash(hash_refresh_token(raw_refresh))

        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Refresh token inválido")
        if token.revoked_at is not None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Refresh token revocado")
        if token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Refresh token expirado")

        self.uow.refresh_tokens.revocar(token)

        roles = self.uow.usuario_roles.get_roles_de_usuario(token.usuario_id)
        return create_access_token(token.usuario_id, roles)

    def logout(self, raw_refresh: str) -> None:
        token = self.uow.refresh_tokens.get_by_hash(hash_refresh_token(raw_refresh))
        if token:
            self.uow.refresh_tokens.revocar(token)

    def me(self, usuario_id: int) -> UsuarioRead:
        usuario = self.uow.usuarios.get_by_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Usuario no encontrado")
        return self._to_read(usuario)
        
    def _to_read(self, usuario: Usuario) -> UsuarioRead:
        roles = self.uow.usuario_roles.get_roles_de_usuario(usuario.id)
        return UsuarioRead(
            id=usuario.id,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            email=usuario.email,
            celular=usuario.celular,
            roles=roles,
            deleted_at=usuario.deleted_at,
        )
    def listar_usuarios(self, offset: int = 0, limit: int = 50) -> list[UsuarioRead]:
        usuarios = self.uow.usuarios.get_all_active(offset, limit)
        return [self._to_read(u) for u in usuarios]
    def asignar_rol(self, usuario_id: int, rol_codigo: str) -> UsuarioRead:
        usuario = self.uow.usuarios.get_by_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        roles_actuales = self.uow.usuario_roles.get_roles_de_usuario(usuario_id)
        if rol_codigo in roles_actuales:
            raise HTTPException(status_code=400, detail="El usuario ya tiene ese rol asignado")

        self.uow.usuario_roles.add(UsuarioRol(usuario_id=usuario_id, rol_codigo=rol_codigo))
        return self._to_read(usuario)

    def quitar_rol(self, usuario_id: int, rol_codigo: str) -> None:
  
    
        usuario = self.uow.usuarios.get_by_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        self.uow.usuario_roles.delete_by_user_and_rol(usuario_id, rol_codigo)
        
    def crear_direccion(self, usuario_id: int, data: DireccionCreate) -> DireccionRead:
        
        direccion = self.uow.direcciones.get_by_id(data.direccion_id)
        if not direccion or direccion.usuario_id != usuario_id or direccion.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La dirección seleccionada es inválida o no pertenece a tu cuenta.",
            )
        
        if data.es_principal:
            self.uow.direcciones.desmarcar_principal(usuario_id)
            
        nueva_dir = DireccionEntrega(**data.model_dump(), usuario_id=usuario_id)
        self.uow.direcciones.add(nueva_dir)
        return DireccionRead.model_validate(nueva_dir)

    def listar_direcciones(self, usuario_id: int) -> list[DireccionRead]:
        direcciones = self.uow.direcciones.get_by_usuario(usuario_id)
        return [DireccionRead.model_validate(d) for d in direcciones]


class DireccionService:
    def __init__(self, uow: UsuarioUnitOfWork):
        self.uow = uow

    def crear_direccion(self, usuario_id: int, data: DireccionCreate) -> DireccionRead:
        # 1. Si el usuario marca esta nueva dirección como principal, 
        # primero desmarcamos las que ya tenga guardadas.
        if data.es_principal:
            self.uow.direcciones.desmarcar_principal(usuario_id)
            
        # 2. Creamos la nueva dirección en la base de datos.
        # Fijate que pasamos el data.model_dump() y le inyectamos el usuario_id
        nueva_dir = DireccionEntrega(**data.model_dump(), usuario_id=usuario_id)
        
        # 3. La agregamos al Unit of Work
        self.uow.direcciones.add(nueva_dir)
        
        # 4. Retornamos la dirección creada
        return DireccionRead.model_validate(nueva_dir)

    def listar_direcciones(self, usuario_id: int) -> list[DireccionRead]:
        direcciones = self.uow.direcciones.get_activas_por_usuario(usuario_id)
        return [DireccionRead.model_validate(d) for d in direcciones]