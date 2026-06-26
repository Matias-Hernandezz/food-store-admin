"""
WebSocket handler para el canal de pedidos en tiempo real.

Extraído de routers.py para cumplir con la arquitectura rúbrica §2.1:
Router → Service → UoW → Repository. El router solo define la ruta y delega.

Autenticación: JWT desde cookie HttpOnly 'access_token' o query param 'token'.
Rooms por rol: role:ADMIN, role:PEDIDOS, role:CLIENT.
Rooms por pedido: order:{pedido_id} (suscripción explícita del cliente).
"""

import asyncio
import json

from fastapi import WebSocket, WebSocketDisconnect
from sqlmodel import Session

from app.core.security import decode_access_token
from app.core.ws_manager import ws_manager
from app.modules.dominio_1.usuarios.repository import UsuarioRepository
from app.modules.dominio_3.pedidos.repository import PedidoRepository


async def handle(websocket: WebSocket, db: Session) -> None:
    """
    Maneja una conexión WebSocket de pedidos de principio a fin:
    - Autentica al usuario vía JWT
    - Registra la conexión en el WSManager con rooms por rol
    - Procesa mensajes entrantes (subscribe-order, unsubscribe-order)
    - Limpia la conexión al desconectarse
    """

    # ── 1. Extraer token ────────────────────────────────────────────────
    token = (
        websocket.query_params.get("token")
        or websocket.cookies.get("access_token")
    )

    if not token:
        await websocket.accept()
        await websocket.close(code=4001, reason="Token requerido")
        return

    # ── 2. Validar JWT ──────────────────────────────────────────────────
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

    # ── 3. Validar usuario en BD ────────────────────────────────────────
    repo_usuario = UsuarioRepository(db)
    user = repo_usuario.get_by_id_with_roles(int(usuario_id))
    if not user or user.deleted_at is not None:
        await websocket.accept()
        await websocket.close(code=4001, reason="Usuario inválido")
        return

    user_id: int = user.id
    roles: list[str] = [rol.codigo.upper() for rol in user.roles]

    # ── 4. Conectar al WSManager con rooms por rol ──────────────────────
    role_rooms = [f"role:{rol}" for rol in roles]
    await ws_manager.connect(websocket, role_rooms)

    # ── 5. Bucle de mensajes con heartbeat ──────────────────────────────
    try:
        await _message_loop(websocket, db, user_id, roles)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)


async def _message_loop(
    websocket: WebSocket,
    db: Session,
    user_id: int,
    roles: list[str],
) -> None:
    """Procesa los mensajes entrantes del WebSocket."""

    while True:
        # Heartbeat cada 30s
        try:
            raw = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
        except asyncio.TimeoutError:
            try:
                await websocket.send_json({"event": "ping"})
            except Exception:
                break
            continue

        # Parsear JSON
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            continue

        action = msg.get("action")

        if action == "subscribe-order":
            await _subscribe_order(websocket, db, user_id, roles, msg)

        elif action == "unsubscribe-order":
            pedido_id = msg.get("pedido_id") or msg.get("order_id")
            if isinstance(pedido_id, int):
                ws_manager.leave_order_room(websocket, pedido_id)


async def _subscribe_order(
    websocket: WebSocket,
    db: Session,
    user_id: int,
    roles: list[str],
    msg: dict,
) -> None:
    """Autoriza y suscribe al WebSocket a la room de un pedido específico."""

    pedido_id = msg.get("pedido_id") or msg.get("order_id")
    if not isinstance(pedido_id, int):
        return

    is_staff = any(rol in {"ADMIN", "PEDIDOS"} for rol in roles)

    # Clientes solo pueden suscribirse a pedidos propios
    if not is_staff:
        repo_pedido = PedidoRepository(db)
        pedido = repo_pedido.get_by_id_con_detalles(pedido_id)
        if not pedido or pedido.usuario_id != user_id:
            await websocket.send_json({
                "event": "ERROR",
                "data": {"detail": "No autorizado para este pedido"},
            })
            return

    ws_manager.join_order_room(websocket, pedido_id)
    await websocket.send_json({
        "event": "SUBSCRIBED",
        "data": {"pedido_id": pedido_id},
    })


# ── Endpoints WS específicos (rúbrica §9.2) ───────────────────────────────────


async def _auth_user(websocket: WebSocket, db: Session) -> dict | None:
    """Autentica al usuario por JWT. Retorna datos del usuario o None (ya cerró la conexión)."""
    token = (
        websocket.query_params.get("token")
        or websocket.cookies.get("access_token")
    )
    if not token:
        await websocket.accept()
        await websocket.close(code=4001, reason="Token requerido")
        return None

    payload = decode_access_token(token)
    if not payload:
        await websocket.accept()
        await websocket.close(code=4001, reason="Token inválido o expirado")
        return None

    usuario_id = payload.get("sub")
    if not usuario_id:
        await websocket.accept()
        await websocket.close(code=4001, reason="Token inválido")
        return None

    repo = UsuarioRepository(db)
    user = repo.get_by_id_with_roles(int(usuario_id))
    if not user or user.deleted_at is not None:
        await websocket.accept()
        await websocket.close(code=4001, reason="Usuario inválido")
        return None

    return {
        "user_id": user.id,
        "roles": [rol.codigo.upper() for rol in user.roles],
    }


async def _heartbeat_loop(websocket: WebSocket) -> None:
    """Loop simple: solo heartbeat, sin procesar mensajes de suscripción."""
    while True:
        try:
            await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
        except asyncio.TimeoutError:
            try:
                await websocket.send_json({"event": "ping"})
            except Exception:
                break
        except WebSocketDisconnect:
            break
        except Exception:
            break


async def handle_pedido(websocket: WebSocket, db: Session, pedido_id: int) -> None:
    """
    Endpoint /ws/pedidos/{pedido_id} — rúbrica §9.2.
    Auto-suscribe al usuario a la room del pedido tras validar propiedad.
    """
    user = await _auth_user(websocket, db)
    if user is None:
        return

    is_staff = any(r in {"ADMIN", "PEDIDOS"} for r in user["roles"])

    if not is_staff:
        repo_pedido = PedidoRepository(db)
        pedido = repo_pedido.get_by_id_con_detalles(pedido_id)
        if not pedido or pedido.usuario_id != user["user_id"]:
            await websocket.accept()
            await websocket.close(code=4003, reason="No autorizado para este pedido")
            return

    await ws_manager.connect(websocket, [f"order:{pedido_id}"])
    await _heartbeat_loop(websocket)
    ws_manager.disconnect(websocket)


async def handle_admin(websocket: WebSocket, db: Session) -> None:
    """
    Endpoint /ws/admin/pedidos — rúbrica §9.2.
    Solo ADMIN y PEDIDOS. Recibe todos los cambios de estado.
    """
    user = await _auth_user(websocket, db)
    if user is None:
        return

    if not any(r in {"ADMIN", "PEDIDOS"} for r in user["roles"]):
        await websocket.accept()
        await websocket.close(code=4003, reason="Rol insuficiente")
        return

    role_rooms = [f"role:{r}" for r in user["roles"] if r in ("ADMIN", "PEDIDOS")]
    await ws_manager.connect(websocket, role_rooms)
    await _heartbeat_loop(websocket)
    ws_manager.disconnect(websocket)
