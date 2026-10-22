import asyncio

from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from sqlmodel import Session

from app.core.ws_manager import ws_manager
from app.modules.public.services import PublicApiService


async def handle_seguimiento(websocket: WebSocket, db: Session, tracking_token: str) -> None:
    """WS público: solo la room del pedido validado por tracking_token."""
    try:
        pedido_id = PublicApiService(db).pedido_id_for_tracking(tracking_token)
    except HTTPException:
        await websocket.accept()
        await websocket.close(code=4004, reason="Pedido no encontrado")
        return

    await websocket.accept()
    await ws_manager.connect(websocket, [f"order:{pedido_id}"])

    try:
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                try:
                    await websocket.send_json({"event": "ping"})
                except Exception:
                    break
    except WebSocketDisconnect:
        pass
    finally:
        ws_manager.disconnect(websocket)
