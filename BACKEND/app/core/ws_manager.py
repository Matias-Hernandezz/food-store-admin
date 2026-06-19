from datetime import datetime, timezone
from typing import Any
from fastapi import WebSocket


class WSManager:
    def __init__(self) -> None:
        self.rooms: dict[str, set[WebSocket]] = {}
        self.socket_rooms: dict[WebSocket, set[str]] = {}

    async def connect(self, websocket: WebSocket, rooms: list[str]) -> None:
        await websocket.accept()
        for room in rooms:
            self._join_room(websocket, room)

    def disconnect(self, websocket: WebSocket) -> None:
        rooms = self.socket_rooms.pop(websocket, set())

        for room in rooms:
            if room in self.rooms:
                self.rooms[room].discard(websocket)
                if not self.rooms[room]:
                    del self.rooms[room]

    async def broadcast_to_room(self, room: str, payload: dict[str, Any]) -> None:
        for connection in list(self.rooms.get(room, set())):
            try:
                await connection.send_json(payload)
            except Exception:
                self.disconnect(connection)

    async def broadcast_to_order(self, pedido_id: int, payload: dict[str, Any]) -> None:
        await self.broadcast_to_room(f"order:{pedido_id}", payload)

    async def broadcast_to_roles(self, roles: list[str], payload: dict[str, Any]) -> None:
        sent_to: set[WebSocket] = set()

        for role in roles:
            room = f"role:{role.upper()}"
            for connection in list(self.rooms.get(room, set())):
                if connection in sent_to:
                    continue

                try:
                    await connection.send_json(payload)
                    sent_to.add(connection)
                except Exception:
                    self.disconnect(connection)

    async def broadcast_pedido(self, pedido_id: int, roles: list[str], payload: dict[str, Any]) -> None:
        await self.broadcast_to_order(pedido_id, payload)
        await self.broadcast_to_roles(roles, payload)

    def join_order_room(self, websocket: WebSocket, pedido_id: int) -> None:
        self._join_room(websocket, f"order:{pedido_id}")

    def leave_order_room(self, websocket: WebSocket, pedido_id: int) -> None:
        room = f"order:{pedido_id}"

        if room in self.rooms:
            self.rooms[room].discard(websocket)
            if websocket in self.socket_rooms:
                self.socket_rooms[websocket].discard(room)
            if not self.rooms[room]:
                del self.rooms[room]

    def _join_room(self, websocket: WebSocket, room: str) -> None:
        self.rooms.setdefault(room, set()).add(websocket)
        self.socket_rooms.setdefault(websocket, set()).add(room)

    @staticmethod
    def make_event(
        event: str,
        pedido_id: int,
        estado_anterior: str | None,
        estado_nuevo: str,
        usuario_id: int | None,
        motivo: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "event": event,
            "pedido_id": pedido_id,
            "estado_anterior": estado_anterior,
            "estado_nuevo": estado_nuevo,
            "usuario_id": usuario_id,
            "motivo": motivo,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }


ws_manager = WSManager()