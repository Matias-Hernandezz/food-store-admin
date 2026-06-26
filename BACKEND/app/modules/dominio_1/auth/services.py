from dataclasses import dataclass

from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_refresh_token,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

from app.modules.dominio_1.auth.unit_of_work import AuthUnitOfWork
from app.modules.dominio_1.auth.models import RefreshToken
from app.modules.dominio_1.auth.schemas import UsuarioCreate

from app.modules.dominio_1.usuarios.models import Usuario, UsuarioRol
from app.modules.dominio_1.usuarios.schemas import UsuarioRead


@dataclass
class LoginResult:
    """Resultado de autenticación: tokens + datos del usuario ya construidos."""
    access_token: str
    refresh_token: str
    usuario_read: UsuarioRead


class AuthService:
    def __init__(self, uow: AuthUnitOfWork) -> None:
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

    def register(self, data: UsuarioCreate) -> UsuarioRead:
        existente = self.uow.usuarios.get_by_email(data.email)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya está registrado",
            )

        usuario = Usuario(
            nombre=data.nombre,
            apellido=data.apellido,
            email=data.email,
            celular=data.celular,
            password_hash=hash_password(data.password),
        )
        self.uow.usuarios.add(usuario)

        rol_cliente = self.uow.roles.get_by_codigo("CLIENT")
        if rol_cliente:
            ur = UsuarioRol(usuario_id=usuario.id, rol_codigo="CLIENT")
            self.uow.usuarios.add(ur)

        return UsuarioRead(
            id=usuario.id,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            email=usuario.email,
            celular=usuario.celular,
            roles=["CLIENT"] if rol_cliente else [],
            created_at=usuario.created_at,
        )

    def login(self, email: str, password: str) -> LoginResult:
        usuario = self.uow.usuarios.get_by_email(email)
        if not usuario or usuario.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
            )

        if not verify_password(password, usuario.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
            )

        roles = self._get_roles(usuario.id)
        access = create_access_token(usuario.id, roles)
        raw_refresh = generate_refresh_token()
        token_hash = hash_refresh_token(raw_refresh)

        refresh = RefreshToken(
            usuario_id=usuario.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.uow.refresh_tokens.add(refresh)

        usuario_read = self.me(usuario.id)
        return LoginResult(
            access_token=access,
            refresh_token=raw_refresh,
            usuario_read=usuario_read,
        )

    def refresh(self, raw_refresh_token: str) -> tuple[str, str]:
        token_hash = hash_refresh_token(raw_refresh_token)
        stored = self.uow.refresh_tokens.get_by_hash(token_hash)

        if not stored or stored.revoked_at is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido o expirado",
            )

        expires = stored.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido o expirado",
            )

        self.uow.refresh_tokens.revocar(stored)

        usuario = self._get_or_404(stored.usuario_id)
        roles = self._get_roles(usuario.id)
        new_access = create_access_token(usuario.id, roles)
        raw_refresh = generate_refresh_token()

        nuevo = RefreshToken(
            usuario_id=usuario.id,
            token_hash=hash_refresh_token(raw_refresh),
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.uow.refresh_tokens.add(nuevo)

        return new_access, raw_refresh

    def logout(self, raw_refresh_token: str) -> None:
        token_hash = hash_refresh_token(raw_refresh_token)
        stored = self.uow.refresh_tokens.get_by_hash(token_hash)
        if stored and stored.revoked_at is None:
            self.uow.refresh_tokens.revocar(stored)

    def me(self, usuario_id: int) -> UsuarioRead:
        usuario = self._get_or_404(usuario_id)
        roles = self._get_roles(usuario_id)
        return UsuarioRead(
            id=usuario.id,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            email=usuario.email,
            celular=usuario.celular,
            roles=roles,
            created_at=usuario.created_at,
        )
