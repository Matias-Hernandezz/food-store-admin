from app.modules.dominio_3.Pedidos.unit_of_work import PedidoUnitOfWork
from app.modules.dominio_1.Usuarios.unit_of_work import UsuarioUnitOfWork
from typing import Annotated
from fastapi import Cookie, Depends, HTTPException, status
from app.core.db import get_session, Session
from typing import Generator
from app.core.security import decode_access_token
from app.core.unit_of_work import UnitOfWork
from app.modules.dominio_1.Usuarios.models import Usuario

def get_uow(session: Session = Depends(get_session)) -> Generator["UnitOfWork", None, None]:
    with UsuarioUnitOfWork(session) as uow:
        yield uow
def get_pedido_uow(session: Session = Depends(get_session)):
    with PedidoUnitOfWork(session) as uow:
        yield uow
async def get_current_user(
    access_token: Annotated[str | None, Cookie()] = None,
    uow: UsuarioUnitOfWork = Depends(get_uow),
) -> Usuario:
   
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado o token expirado",
    )

    if access_token is None:
        raise credentials_exception

    payload = decode_access_token(access_token)
    if payload is None:
        raise credentials_exception

    usuario_id: str | None = payload.get("sub")
    if usuario_id is None:
        raise credentials_exception

    user = uow.usuarios.get_by_id(int(usuario_id))

    if user is None:
        raise credentials_exception

    return user


async def get_active_user(
    current_user: Annotated[Usuario, Depends(get_current_user)],
) -> Usuario:
    if current_user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cuenta eliminada",
        )
    return current_user


def require_role(allowed_roles: list[str]):
    async def checker(
        access_token: Annotated[str | None, Cookie()] = None,
    ) -> None:
        if access_token is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="No autenticado")

        payload = decode_access_token(access_token)
        if payload is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Token inválido")

        user_roles: list[str] = payload.get("roles", [])
        if not any(r in allowed_roles for r in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rol insuficiente. Se requiere: {allowed_roles}",
            )

    return checker