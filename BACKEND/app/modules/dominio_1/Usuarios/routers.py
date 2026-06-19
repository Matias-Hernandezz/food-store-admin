
from app.modules.dominio_1.Usuarios.schemas import DireccionCreate, DireccionRead, LoginResponse, UsuarioUpdate
from app.core.deps import require_role
from typing import Annotated
from app.core.security import decode_access_token
from fastapi import APIRouter, Cookie, Depends, Response, status, Request
from app.core.deps import get_active_user, get_uow
from app.core.security import COOKIE_ACCESS, COOKIE_REFRESH, REFRESH_TOKEN_EXPIRE_DAYS
from app.modules.dominio_1.Usuarios.unit_of_work import UsuarioUnitOfWork
from app.modules.dominio_1.Usuarios.models import Usuario
from app.modules.dominio_1.Usuarios.schemas import LoginInput, UsuarioCreate, UsuarioRead
from app.modules.dominio_1.Usuarios.services import AuthService, DireccionService
from app.core.rate_limit import limiter
from pydantic import BaseModel
from fastapi import HTTPException

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])
_ACCESS_MAX_AGE  = 30 * 60
_REFRESH_MAX_AGE = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60


def _set_cookies(response: Response, access: str, refresh: str) -> None:
    response.set_cookie(
        key=COOKIE_ACCESS,
        value=access,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
        max_age=_ACCESS_MAX_AGE,
    )
    response.set_cookie(
        key=COOKIE_REFRESH,
        value=refresh,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=_REFRESH_MAX_AGE,
        path="/api/v1/auth/refresh",
    )


def _clear_cookies(response: Response) -> None:
    
    response.delete_cookie(COOKIE_ACCESS)
    response.delete_cookie(COOKIE_REFRESH, path="/api/v1/auth/refresh")




@router.post("/register", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/15minutes")
def register(
    request: Request,
    data: UsuarioCreate,
    uow: UsuarioUnitOfWork = Depends(get_uow),
):
    with uow:
        return AuthService(uow).register(data)


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/15minutes")
def login(
    request: Request,
    data: LoginInput,
    response: Response,
    uow: UsuarioUnitOfWork = Depends(get_uow),
):
    with uow:
        svc = AuthService(uow)
        access, refresh = svc.login(str(data.email), data.password)
        usuario_id = int(decode_access_token(access)["sub"])
        usuario_read = svc.me(usuario_id)

    _set_cookies(response, access, refresh)
    return LoginResponse(
        id=usuario_read.id,
        nombre=usuario_read.nombre,
        apellido=usuario_read.apellido,
        email=usuario_read.email,
        celular=usuario_read.celular,
        roles=usuario_read.roles,
        created_at=usuario_read.created_at,
        deleted_at=usuario_read.deleted_at,
        access_token=access,
        refresh_token=refresh,
        token_type="bearer",
        expires_in=_ACCESS_MAX_AGE,
    )


@router.post("/refresh", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
def refresh(
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    uow: UsuarioUnitOfWork = Depends(get_uow),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Sin refresh token")

    with uow:
        new_access = AuthService(uow).refresh(refresh_token)

    response.set_cookie(
        key=COOKIE_ACCESS,
        value=new_access,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=_ACCESS_MAX_AGE,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    uow: UsuarioUnitOfWork = Depends(get_uow),
):
    if refresh_token:
        with uow:
            AuthService(uow).logout(refresh_token)
    _clear_cookies(response)


@router.get("/me", response_model=UsuarioRead)
def me(
    current_user: Annotated[Usuario, Depends(get_active_user)],
    uow: UsuarioUnitOfWork = Depends(get_uow),
):
    with uow:
        return AuthService(uow).me(current_user.id)
@router.get("/usuarios", response_model=list[UsuarioRead], dependencies=[Depends(require_role(["ADMIN"]))])
def listar_usuarios_admin(
    offset: int = 0,
    limit: int = 50,
    search: str | None = None,
    uow: UsuarioUnitOfWork = Depends(get_uow),
):
    with uow:
        return AuthService(uow).listar_usuarios(offset, limit, search)


@router.patch("/usuarios/{usuario_id}", response_model=UsuarioRead, dependencies=[Depends(require_role(["ADMIN"]))])
def actualizar_usuario(
    usuario_id: int,
    data: UsuarioUpdate,
    uow: UsuarioUnitOfWork = Depends(get_uow),
):
    with uow:
        return AuthService(uow).actualizar_usuario(usuario_id, data)


@router.delete("/usuarios/{usuario_id}", status_code=204, dependencies=[Depends(require_role(["ADMIN"]))])
def eliminar_usuario(
    usuario_id: int,
    uow: UsuarioUnitOfWork = Depends(get_uow),
):
    with uow:
        AuthService(uow).soft_delete_usuario(usuario_id)


class RolInput(BaseModel):
    rol_codigo: str

@router.post("/usuarios/{usuario_id}/roles", response_model=UsuarioRead, dependencies=[Depends(require_role(["ADMIN"]))])
def asignar_rol(
    usuario_id: int,
    data: RolInput,
    current_user: Annotated[Usuario, Depends(get_active_user)], 
    uow: UsuarioUnitOfWork = Depends(get_uow),
):
    with uow:
        return AuthService(uow).asignar_rol(usuario_id, data.rol_codigo)

@router.delete("/usuarios/{user_id}/roles/{rol_codigo}", status_code=204)
def quitar_rol(
    user_id: int,
    rol_codigo: str,
    _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))],
    uow: UsuarioUnitOfWork = Depends(get_uow),
):
    with uow:
        uow.usuario_roles.eliminar(user_id, rol_codigo)

@router.post("/direccion", response_model=DireccionRead)
def crear_direccion_usuario(
    data: DireccionCreate,
    current_user: Annotated[Usuario, Depends(get_active_user)],
    uow: UsuarioUnitOfWork = Depends(get_uow),
):
    with uow:
        return DireccionService(uow).crear_direccion(current_user.id, data)
@router.get("/token")

def token_para_ws(
    access_token: Annotated[str | None, Cookie()] = None,
):
    """Devuelve el access token para que el frontend pueda usarlo en WebSocket."""
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    return {"access_token": access_token}

@router.patch("/direcciones/{direccion_id}/principal", response_model=DireccionRead)
def establecer_direccion_principal(
    direccion_id: int,
    current_user: Annotated[Usuario, Depends(get_active_user)],
    uow: UsuarioUnitOfWork = Depends(get_uow),
):
    with uow:
        return DireccionService(uow).establecer_principal(current_user.id, direccion_id)


@router.get("/direcciones", response_model=list[DireccionRead])
def listar(
    current_user: Annotated[Usuario, Depends(get_active_user)],
    uow: UsuarioUnitOfWork = Depends(get_uow),
):
    with uow:
        return DireccionService(uow).listar_direcciones(current_user.id)
