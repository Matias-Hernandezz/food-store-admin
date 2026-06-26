from typing import Generator

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.deps import require_role

from app.modules.dominio_1.usuarios.unit_of_work import UsuarioUnitOfWork
from app.modules.dominio_1.usuarios.schemas import UsuarioRead, UsuarioUpdate
from app.modules.dominio_1.usuarios.services import UsuarioService

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])


def get_usuario_uow(
    session: Session = Depends(get_session),
) -> Generator[UsuarioUnitOfWork, None, None]:
    with UsuarioUnitOfWork(session) as uow:
        yield uow


@router.get(
    "/",
    response_model=list[UsuarioRead],
    dependencies=[Depends(require_role(["ADMIN"]))],
)
def listar_usuarios(
    search: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    uow: UsuarioUnitOfWork = Depends(get_usuario_uow),
):
    with uow:
        return UsuarioService(uow).listar_usuarios(search=search, offset=offset, limit=limit)


@router.patch(
    "/{id}",
    response_model=UsuarioRead,
    dependencies=[Depends(require_role(["ADMIN"]))],
)
def actualizar_usuario(
    id: int,
    data: UsuarioUpdate,
    uow: UsuarioUnitOfWork = Depends(get_usuario_uow),
):
    with uow:
        return UsuarioService(uow).actualizar_usuario(id, data)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(["ADMIN"]))],
)
def soft_delete_usuario(
    id: int,
    uow: UsuarioUnitOfWork = Depends(get_usuario_uow),
):
    with uow:
        UsuarioService(uow).soft_delete_usuario(id)


@router.post(
    "/{id}/roles",
    response_model=UsuarioRead,
    dependencies=[Depends(require_role(["ADMIN"]))],
)
def asignar_rol(
    id: int,
    rol_codigo: str = Query(..., description="Código del rol a asignar"),
    uow: UsuarioUnitOfWork = Depends(get_usuario_uow),
):
    with uow:
        return UsuarioService(uow).asignar_rol(id, rol_codigo)


@router.delete(
    "/{id}/roles/{rol_codigo}",
    response_model=UsuarioRead,
    dependencies=[Depends(require_role(["ADMIN"]))],
)
def quitar_rol(
    id: int,
    rol_codigo: str,
    uow: UsuarioUnitOfWork = Depends(get_usuario_uow),
):
    with uow:
        return UsuarioService(uow).quitar_rol(id, rol_codigo)
