import pytest

from app.core.ws_manager import ws_manager


def test_rooms_for_pedido_incluye_order_y_roles():
    rooms = ws_manager.rooms_for_pedido(42, ["owner", "KITCHEN"])
    assert rooms == ["order:42", "role:OWNER", "role:KITCHEN"]


@pytest.mark.asyncio
async def test_publish_ws_event_sin_redis_entrega_local(monkeypatch):
    from app.core import ws_redis

    monkeypatch.setattr(ws_redis, "redis_enabled", lambda: False)

    delivered: list[str] = []

    async def fake_broadcast(room: str, payload: dict):
        delivered.append(room)

    monkeypatch.setattr(
        ws_manager,
        "broadcast_to_room",
        fake_broadcast,
    )

    await ws_redis.publish_ws_event(["order:1"], {"event": "test"})
    assert delivered == ["order:1"]
