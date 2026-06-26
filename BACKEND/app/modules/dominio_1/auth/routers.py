from typing import Annotated, Generator

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Request, Response, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.deps import get_active_user, require_role
from app.core.security import (
    COOKIE_ACCESS,
    COOKIE_REFRESH,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from app.core.rate_limit import limiter

from app.modules.dominio_1.auth.unit_of_work import AuthUnitOfWork
from app.modules.dominio_1.auth.schemas import LoginInput, LoginResponse, TokenResponse, UsuarioCreate
from app.modules.dominio_1.auth.services import AuthService

from app.modules.dominio_1.usuarios.models import Usuario
from app.modules.dominio_1.usuarios.schemas import UsuarioRead

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

_ACCESS_MAX_AGE = 30 * 60
_REFRESH_MAX_AGE = 7 * 24 * 60 * 60


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


def get_auth_uow(session: Session = Depends(get_session)) -> Generator[AuthUnitOfWork, None, None]:
    with AuthUnitOfWork(session) as uow:
        yield uow


# ── Auth endpoints ───────────────────────────────────────────────────────────

@router.post("/register", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/15minutes")
def register(
    request: Request,
    data: UsuarioCreate,
    uow: AuthUnitOfWork = Depends(get_auth_uow),
):
    with uow:
        return AuthService(uow).register(data)


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/15minutes")
def login(
    request: Request,
    data: LoginInput,
    response: Response,
    uow: AuthUnitOfWork = Depends(get_auth_uow),
):
    with uow:
        result = AuthService(uow).login(str(data.email), data.password)

    _set_cookies(response, result.access_token, result.refresh_token)
    return LoginResponse(
        id=result.usuario_read.id,
        nombre=result.usuario_read.nombre,
        apellido=result.usuario_read.apellido,
        email=result.usuario_read.email,
        celular=result.usuario_read.celular,
        roles=result.usuario_read.roles,
        created_at=result.usuario_read.created_at,
        deleted_at=result.usuario_read.deleted_at,
        token_type="bearer",
        expires_in=_ACCESS_MAX_AGE,
    )


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def refresh(
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    uow: AuthUnitOfWork = Depends(get_auth_uow),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Sin refresh token")

    with uow:
        new_access, new_refresh = AuthService(uow).refresh(refresh_token)
    _set_cookies(response, new_access, new_refresh)
    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
        expires_in=_ACCESS_MAX_AGE,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    uow: AuthUnitOfWork = Depends(get_auth_uow),
):
    if refresh_token:
        with uow:
            AuthService(uow).logout(refresh_token)
    response.delete_cookie(COOKIE_ACCESS, path="/")
    response.delete_cookie(COOKIE_REFRESH, path="/api/v1/auth/refresh")


@router.get("/me", response_model=UsuarioRead)
def me(
    current_user: Annotated[Usuario, Depends(get_active_user)],
    uow: AuthUnitOfWork = Depends(get_auth_uow),
):
    with uow:
        return AuthService(uow).me(int(current_user.id))


@router.get("/token")
def token_para_ws(
    access_token: Annotated[str | None, Cookie()] = None,
):
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    return {"access_token": access_token}
