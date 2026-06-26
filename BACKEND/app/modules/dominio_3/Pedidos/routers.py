# app/modules/dominio_3/pedidos/routers.py

from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, WebSocket, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.deps import get_active_user, get_pedido_uow, require_role
from app.core.unit_of_work import UnitOfWork
from app.modules.dominio_1.usuarios.models import Usuario
from app.modules.dominio_3.pedidos.schemas import (
    AvanzarEstadoInput,
    FormaPagoRead,
    HistorialRead,
    PedidoCreate,
    PedidoList,
    PedidoRead,
)
from app.modules.dominio_3.pedidos.services import PedidoService
from app.modules.dominio_3.pedidos.ws_handler import handle as ws_handle
from app.modules.dominio_3.pedidos.ws_handler import handle_pedido as ws_handle_pedido
from app.modules.dominio_3.pedidos.ws_handler import handle_admin as ws_handle_admin

router = APIRouter(prefix="/api/v1/pedidos", tags=["Pedidos"])


def _roles_from_user(current_user: Usuario) -> list[str]:
    """Extrae los códigos de rol del usuario autenticado."""
    return [rol.codigo for rol in current_user.roles]


# ─── REST endpoints ───────────────────────────────────────────────────────────

@router.get(
    "/formas-pago",
    response_model=list[FormaPagoRead],
    summary="Listar formas de pago habilitadas",
)
def listar_formas_pago(uow: UnitOfWork = Depends(get_pedido_uow)):
    with uow:
        return uow.formas_pago.get_habilitadas()


@router.post(
        "/",
        response_model=PedidoRead,
        status_code=status.HTTP_201_CREATED,
        summary="Crear pedido desde el carrito",
        dependencies=[Depends(require_role(["ADMIN", "PEDIDOS", "CLIENT"]))],
    )
async def crear_pedido(    # ← async para poder await el emit
    data: PedidoCreate,
    current_user: Annotated[Usuario, Depends(get_active_user)],
    uow: UnitOfWork = Depends(get_pedido_uow),
):
    with uow:
        result = PedidoService(uow).crear(data, current_user.id)

    # ✅ broadcast FUERA del bloque UoW — el staff ve el pedido nuevo al instante
    await PedidoService.emitir_evento_estado_pedido(
        pedido=result.pedido,
        estado_anterior=result.estado_anterior,   # None
        usuario_id=current_user.id,
        motivo=None,
    )

    return result.pedido


@router.get(
        "/",
        response_model=PedidoList,
        summary="Listar pedidos: CLIENT ve propios, ADMIN/PEDIDOS ven todos",
        dependencies=[Depends(require_role(["ADMIN", "PEDIDOS", "CLIENT"]))],
    )
def listar_pedidos(
        current_user: Annotated[Usuario, Depends(get_active_user)],
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=100),
        desde: Optional[date] = Query(default=None, description="Filtrar desde fecha (YYYY-MM-DD)"),
        hasta: Optional[date] = Query(default=None, description="Filtrar hasta fecha (YYYY-MM-DD)"),
        search: Optional[str] = Query(default=None, description="Buscar por nombre de usuario"),
        estado: Optional[str] = Query(default=None, description="Filtrar por estado (PENDIENTE, CONFIRMADO, EN_PREP, ENTREGADO, CANCELADO)"),
        uow: UnitOfWork = Depends(get_pedido_uow),
    ):
        roles = _roles_from_user(current_user)
        with uow:
            return PedidoService(uow).listar(
                usuario_id=current_user.id,
                roles=roles,
                offset=offset,
                limit=limit,
                desde=desde,
                hasta=hasta,
                search=search,
                estado=estado,
            )

@router.get(
        "/cocina",
        response_model=PedidoList,
        summary="Listar pedidos asignados a la cocina (CONFIRMADO y EN_PREP)",
        dependencies=[Depends(require_role(["ADMIN", "PEDIDOS"]))], )
def listar_pedidos_cocina(
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=50, ge=1, le=100),
        desde: Optional[date] = Query(default=None, description="Filtrar desde fecha"),
        hasta: Optional[date] = Query(default=None, description="Filtrar hasta fecha"),
        uow: UnitOfWork = Depends(get_pedido_uow),
    ):
        with uow:
            return PedidoService(uow).listar_cocina(
                offset=offset, limit=limit,
                desde=desde, hasta=hasta,
            )
  

@router.get(
        "/{pedido_id}",
        response_model=PedidoRead,
        summary="Obtener detalle de un pedido",
        dependencies=[Depends(require_role(["ADMIN", "PEDIDOS", "CLIENT"]))],
    )
def obtener_pedido(
        pedido_id: int,
        current_user: Annotated[Usuario, Depends(get_active_user)],
        uow: UnitOfWork = Depends(get_pedido_uow),
    ):
        roles = _roles_from_user(current_user)
        with uow:
            return PedidoService(uow).obtener(
                pedido_id=pedido_id,
                usuario_id=current_user.id,
                roles=roles,
            )


@router.get(
        "/{pedido_id}/historial",
        response_model=list[HistorialRead],
        summary="Historial de estados del pedido",
        dependencies=[Depends(require_role(["ADMIN", "PEDIDOS", "CLIENT"]))],
    )
def historial_pedido(
    pedido_id: int,
    uow: UnitOfWork = Depends(get_pedido_uow),
):
    with uow:
        return PedidoService(uow).historial(pedido_id)


@router.patch(
    "/{pedido_id}/estado",
    response_model=PedidoRead,
    summary="Avanzar estado del pedido",
    dependencies=[Depends(require_role(["ADMIN", "PEDIDOS"]))],
)
async def avanzar_estado(
    pedido_id: int,
    data: AvanzarEstadoInput,
    current_user: Annotated[Usuario, Depends(get_active_user)],
    uow: UnitOfWork = Depends(get_pedido_uow),
):
    roles = _roles_from_user(current_user)

    with uow:
        result = PedidoService(uow).avanzar_estado(
            pedido_id=pedido_id,
            nuevo_estado=data.nuevo_estado,
            actor_id=current_user.id,
            roles=roles,
            data=data,
        )

    # ✅ broadcast FUERA del bloque UoW (post-commit)
    await PedidoService.emitir_evento_estado_pedido(
        pedido=result.pedido,
        estado_anterior=result.estado_anterior,
        usuario_id=current_user.id,
        motivo=data.motivo,
    )

    return result.pedido


@router.delete(
    "/{pedido_id}",
    response_model=PedidoRead,
    summary="Cancelar pedido propio",
    dependencies=[Depends(require_role(["CLIENT"]))],
)
async def cancelar_pedido_propio(
    pedido_id: int,
    data: AvanzarEstadoInput,
    current_user: Annotated[Usuario, Depends(get_active_user)],
    uow: UnitOfWork = Depends(get_pedido_uow),
):
    data.nuevo_estado = "CANCELADO"

    with uow:
        result = PedidoService(uow).avanzar_estado(
            pedido_id=pedido_id,
            nuevo_estado="CANCELADO",
            actor_id=current_user.id,
            roles=["CLIENT"],
            data=data,
        )

    # ✅ broadcast FUERA del bloque UoW (post-commit)
    await PedidoService.emitir_evento_estado_pedido(
        pedido=result.pedido,
        estado_anterior=result.estado_anterior,
        usuario_id=current_user.id,
        motivo=data.motivo,
    )

    return result.pedido


# ─── WebSocket ────────────────────────────────────────────────────────────────

@router.websocket("/ws/pedidos")
async def pedidos_ws(
    websocket: WebSocket,
    db: Session = Depends(get_session),
):
    """
    Canal bidireccional autenticado para notificaciones en tiempo real.
    Delega toda la lógica (auth, user lookup, rooms, message loop) al handler.
    """
    await ws_handle(websocket, db)


@router.websocket("/ws/pedidos/{pedido_id}")
async def pedido_ws(
    pedido_id: int,
    websocket: WebSocket,
    db: Session = Depends(get_session),
):
    """
    Canal para seguir un pedido específico — rúbrica §9.2.
    Auto-suscribe al usuario a la room del pedido.
    """
    await ws_handle_pedido(websocket, db, pedido_id)


@router.websocket("/ws/admin/pedidos")
async def admin_pedidos_ws(
    websocket: WebSocket,
    db: Session = Depends(get_session),
):
    """
    Canal exclusivo para administradores y gestores de pedidos — rúbrica §9.2.
    Solo roles ADMIN y PEDIDOS.
    """
    await ws_handle_admin(websocket, db)
