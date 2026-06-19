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
from app.modules.dominio_1.Usuarios.schemas import UsuarioCreate, UsuarioRead, UsuarioUpdate
from app.modules.dominio_1.Usuarios.unit_of_work import UsuarioUnitOfWork

class AuthService:
    """Servicio de autenticación y autorización.

    Gestiona registro, login, refresh de JWT, logout y operaciones CRUD
    de usuarios. Opera dentro del Unit of Work provisto por el router.
    """

    def __init__(self, uow: UsuarioUnitOfWork):
        self.uow = uow

    # ── register ────────────────────────────────────────────────────────
    def register(self, data: UsuarioCreate) -> UsuarioRead:
        """Registra un nuevo usuario con rol CLIENT por defecto."""
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
        """Autentica al usuario y retorna (access_token, refresh_token)."""
        usuario = self.uow.usuarios.get_by_email(email)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no registrado",
            )

        if not verify_password(password, usuario.password_hash):
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
            created_at=usuario.created_at,
            deleted_at=usuario.deleted_at,
        )
    def listar_usuarios(self, offset: int = 0, limit: int = 50, search: str | None = None) -> list[UsuarioRead]:
        usuarios = self.uow.usuarios.get_all_active(offset, limit, search)
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

    def actualizar_usuario(self, usuario_id: int, data: UsuarioUpdate) -> UsuarioRead:
        usuario = self.uow.usuarios.get_by_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        patch = data.model_dump(exclude_unset=True)
        for field, value in patch.items():
            setattr(usuario, field, value)
        self.uow.usuarios.update(usuario)
        return self._to_read(usuario)

    def soft_delete_usuario(self, usuario_id: int) -> None:
        usuario = self.uow.usuarios.get_by_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        self.uow.usuarios.soft_delete(usuario)

    def quitar_rol(self, usuario_id: int, rol_codigo: str) -> None:
  
    
        usuario = self.uow.usuarios.get_by_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        self.uow.usuario_roles.eliminar(usuario_id, rol_codigo)


class DireccionService:
    def __init__(self, uow: UsuarioUnitOfWork):
        self.uow = uow

    def crear_direccion(self, usuario_id: int, data: DireccionCreate) -> DireccionRead:
        direccion = DireccionEntrega(
            usuario_id=usuario_id,
            alias=data.alias,
            linea1=data.linea1,
            linea2=data.linea2,
            ciudad=data.ciudad,
            provincia=data.provincia,
            codigo_postal=data.codigo_postal,
            latitud=data.latitud,
            longitud=data.longitud,
        )
        direccion = self.uow.direcciones.add(direccion)
        return DireccionRead.model_validate(direccion)

    def listar_direcciones(self, usuario_id: int) -> list[DireccionRead]:
        direcciones = self.uow.direcciones.get_activas_por_usuario(usuario_id)
        return [DireccionRead.model_validate(d) for d in direcciones]

    def establecer_principal(self, usuario_id: int, direccion_id: int) -> DireccionRead:
        direccion = self.uow.direcciones.get_by_id(direccion_id)
        if not direccion:
            raise HTTPException(status_code=404, detail="Dirección no encontrada")
        if direccion.usuario_id != usuario_id:
            raise HTTPException(status_code=403, detail="La dirección no pertenece a este usuario")
        if direccion.deleted_at is not None:
            raise HTTPException(status_code=400, detail="No se puede establecer como principal una dirección eliminada")

        # Desmarcar todas las principales del usuario
        self.uow.direcciones.desmarcar_principal(usuario_id)

        # Marcar esta como principal
        direccion.es_principal = True
        direccion = self.uow.direcciones.update(direccion)

        return DireccionRead.model_validate(direccion)

