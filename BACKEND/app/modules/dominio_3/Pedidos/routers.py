# app/modules/dominio_3/Pedidos/router.py

import json
from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Cookie, Depends, Query, WebSocket, WebSocketDisconnect, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.ws_manager import ws_manager          # tu WSManager singleton
from app.core.deps import get_active_user, get_pedido_uow, require_role
from app.core.security import decode_access_token
from app.core.unit_of_work import UnitOfWork
from app.modules.dominio_3.Pedidos.unit_of_work import PedidoUnitOfWork
from app.modules.dominio_1.Usuarios.models import Usuario
from app.modules.dominio_1.Usuarios.repository import UsuarioRepository
from app.modules.dominio_3.Pedidos.repository import PedidoRepository
from app.modules.dominio_3.Pedidos.schemas import (
    AvanzarEstadoInput,
    FormaPagoRead,
    HistorialRead,
    PedidoCreate,
    PedidoList,
    PedidoRead,
)
from app.modules.dominio_3.Pedidos.services import PedidoService

router = APIRouter(prefix="/api/v1/pedidos", tags=["Pedidos"])


# ─── helpers ──────────────────────────────────────────────────────────────────

def _get_roles(access_token: str | None) -> list[str]:
    if not access_token:
        return []
    payload = decode_access_token(access_token)
    if not payload:
        return []
    return payload.get("roles", [])


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
    access_token: Annotated[str | None, Cookie()] = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    desde: Optional[date] = Query(default=None, description="Filtrar desde fecha (YYYY-MM-DD)"),
    hasta: Optional[date] = Query(default=None, description="Filtrar hasta fecha (YYYY-MM-DD)"),
    search: Optional[str] = Query(default=None, description="Buscar por nombre de usuario"),
    estado: Optional[str] = Query(default=None, description="Filtrar por estado (PENDIENTE, CONFIRMADO, EN_PREP, ENTREGADO, CANCELADO)"),
    uow: UnitOfWork = Depends(get_pedido_uow),
):
    roles = _get_roles(access_token)
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
    dependencies=[Depends(require_role(["ADMIN", "PEDIDOS"]))], 
)
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
    access_token: Annotated[str | None, Cookie()] = None,
    uow: UnitOfWork = Depends(get_pedido_uow),
):
    roles = _get_roles(access_token)
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
    access_token: Annotated[str | None, Cookie()] = None,
    uow: UnitOfWork = Depends(get_pedido_uow),
):
    roles = _get_roles(access_token)
    nuevo_estado = data.nuevo_estado.upper()

    with uow:
        result = PedidoService(uow).avanzar_estado(
            pedido_id=pedido_id,
            nuevo_estado=nuevo_estado,
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

    Autenticación: JWT desde cookie HttpOnly 'access_token' o query param 'token'.
    Rooms por rol:  role:ADMIN, role:PEDIDOS, role:CLIENT, etc.
    Rooms por pedido: order:{pedido_id} (suscripción explícita del cliente).
    """
    from sqlmodel import Session  # type hint, no-op at runtime

    # 1. Extraer token ────────────────────────────────────────────────────────
    token = (
        websocket.query_params.get("token")
        or websocket.cookies.get("access_token")
    )

    if not token:
        await websocket.accept()
        await websocket.close(code=4001, reason="Token requerido")
        return

    # 2. Validar JWT ──────────────────────────────────────────────────────────
    payload = decode_access_token(token)
    if not payload:
        await websocket.accept()
        await websocket.close(code=4001, reason="Token inválido o expirado")
        return

    usuario_id = payload.get("sub")
    if not usuario_id:
        await websocket.accept()
        await websocket.close(code=4001, reason="Token inválido")
        return

    # 3. Validar usuario en BD ────────────────────────────────────────────────
    repo = UsuarioRepository(db)
    user = repo.get_by_id_with_roles(int(usuario_id))
    if not user or user.deleted_at is not None:
        await websocket.accept()
        await websocket.close(code=4001, reason="Usuario inválido")
        return

    user_id: int = user.id
    # Normalizar roles a mayúsculas para las rooms
    roles: list[str] = [rol.codigo.upper() for rol in user.roles]

    # 4. Conectar al WSManager con rooms por rol ───────────────────────────────
    # Cada rol tiene su propia room: role:ADMIN, role:PEDIDOS, etc.
    role_rooms = [f"role:{rol}" for rol in roles]
    await ws_manager.connect(websocket, role_rooms)

    # 5. Bucle de mensajes ────────────────────────────────────────────────────
    try:
        while True:
            raw = await websocket.receive_text()

            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            action = msg.get("action")

            # ── subscribe-order ──────────────────────────────────────────────
            if action == "subscribe-order":
                pedido_id = msg.get("pedido_id") or msg.get("order_id")
                if not isinstance(pedido_id, int):
                    continue

                is_staff = any(rol in {"ADMIN", "PEDIDOS"} for rol in roles)

                # Los clientes solo pueden suscribirse a pedidos propios
                if not is_staff:
                    repo_pedido = PedidoRepository(db)
                    pedido = repo_pedido.get_by_id_con_detalles(pedido_id)
                    if not pedido or pedido.usuario_id != user_id:
                        await websocket.send_json({
                            "event": "ERROR",
                            "data": {"detail": "No autorizado para este pedido"},
                        })
                        continue

                ws_manager.join_order_room(websocket, pedido_id)
                await websocket.send_json({
                    "event": "SUBSCRIBED",
                    "data": {"pedido_id": pedido_id},
                })

            # ── unsubscribe-order ────────────────────────────────────────────
            elif action == "unsubscribe-order":
                pedido_id = msg.get("pedido_id") or msg.get("order_id")
                if isinstance(pedido_id, int):
                    ws_manager.leave_order_room(websocket, pedido_id)

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
