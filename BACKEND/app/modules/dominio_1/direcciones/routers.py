from typing import Annotated, Generator

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.deps import get_active_user

from app.modules.dominio_1.direcciones.unit_of_work import DireccionUnitOfWork
from app.modules.dominio_1.direcciones.schemas import DireccionCreate, DireccionRead
from app.modules.dominio_1.direcciones.services import DireccionService

from app.modules.dominio_1.usuarios.models import Usuario

router = APIRouter(prefix="/api/v1/direcciones", tags=["Direcciones"])


def get_direccion_uow(
    session: Session = Depends(get_session),
) -> Generator[DireccionUnitOfWork, None, None]:
    with DireccionUnitOfWork(session) as uow:
        yield uow


@router.post("/", response_model=DireccionRead, status_code=status.HTTP_201_CREATED)
def crear_direccion(
    data: DireccionCreate,
    current_user: Annotated[Usuario, Depends(get_active_user)],
    uow: DireccionUnitOfWork = Depends(get_direccion_uow),
):
    with uow:
        return DireccionService(uow).crear_direccion(int(current_user.id), data)


@router.get("/", response_model=list[DireccionRead])
def listar_direcciones(
    current_user: Annotated[Usuario, Depends(get_active_user)],
    uow: DireccionUnitOfWork = Depends(get_direccion_uow),
):
    with uow:
        return DireccionService(uow).listar_direcciones(int(current_user.id))


@router.patch("/{id}/principal", response_model=DireccionRead)
def establecer_principal(
    id: int,
    current_user: Annotated[Usuario, Depends(get_active_user)],
    uow: DireccionUnitOfWork = Depends(get_direccion_uow),
):
    with uow:
        return DireccionService(uow).establecer_principal(int(current_user.id), id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_direccion(
    id: int,
    current_user: Annotated[Usuario, Depends(get_active_user)],
    uow: DireccionUnitOfWork = Depends(get_direccion_uow),
):
    with uow:
        DireccionService(uow).eliminar_direccion(int(current_user.id), id)
