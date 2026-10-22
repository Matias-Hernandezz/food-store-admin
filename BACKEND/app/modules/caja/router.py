from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.deps import get_active_user, require_role
from app.core.roles import CASHIER as ROLE_CASHIER, OWNER as ROLE_OWNER
from app.modules.dominio_3.pedidos.schemas import PedidoRead
from app.modules.caja.schemas import (
    AbrirTurnoInput,
    CerrarTurnoInput,
    PedidoMostradorInput,
    PedidoMostradorResult,
    TurnoCajaRead,
)
from app.modules.caja.service import CajaService
from app.modules.dominio_1.usuarios.models import Usuario

router = APIRouter(
    prefix="/api/v1/caja",
    tags=["Caja"],
    dependencies=[Depends(require_role([ROLE_OWNER, ROLE_CASHIER]))],
)


@router.get("/turno/actual", response_model=TurnoCajaRead | None)
def turno_actual(
    _user: Annotated[Usuario, Depends(get_active_user)],
    session: Session = Depends(get_session),
):
    return CajaService(session).turno_actual()


@router.post("/turno/abrir", response_model=TurnoCajaRead, status_code=status.HTTP_201_CREATED)
def abrir_turno(
    body: AbrirTurnoInput,
    user: Annotated[Usuario, Depends(get_active_user)],
    session: Session = Depends(get_session),
):
    return CajaService(session).abrir_turno(user.id, body)


@router.post("/turno/cerrar", response_model=TurnoCajaRead)
def cerrar_turno(
    body: CerrarTurnoInput,
    user: Annotated[Usuario, Depends(get_active_user)],
    session: Session = Depends(get_session),
):
    return CajaService(session).cerrar_turno(user.id, body)


@router.post("/pedidos-mostrador", response_model=PedidoMostradorResult, status_code=status.HTTP_201_CREATED)
async def pedido_mostrador(
    body: PedidoMostradorInput,
    user: Annotated[Usuario, Depends(get_active_user)],
    session: Session = Depends(get_session),
):
    return await CajaService(session).crear_pedido_mostrador(user, body)


@router.post("/pedidos/{pedido_id}/confirmar-cobro", response_model=PedidoRead)
async def confirmar_cobro_pedido(
    pedido_id: int,
    user: Annotated[Usuario, Depends(get_active_user)],
    session: Session = Depends(get_session),
):
    return await CajaService(session).confirmar_cobro_pedido(user, pedido_id)
