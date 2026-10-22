"""Puente Redis pub/sub para WebSocket multi-worker."""

import asyncio
import json
import logging
from typing import Any

from app.core.config import settings
from app.core.tenant.context import get_current_tenant_slug

logger = logging.getLogger(__name__)

_redis_client = None
_pubsub_task: asyncio.Task | None = None


def resolve_ws_channel(tenant_slug: str | None = None) -> str:
    slug = tenant_slug or get_current_tenant_slug()
    if slug:
        return f"{settings.redis_ws_channel}:{slug}"
    return settings.redis_ws_channel


def redis_enabled() -> bool:
    return bool(settings.redis_url.strip())


async def start_ws_redis_bridge() -> None:
    """Suscribe este worker al canal WS y reenvía a conexiones locales."""
    global _redis_client, _pubsub_task

    if not redis_enabled():
        logger.info("Redis WS: deshabilitado (REDIS_URL vacío)")
        return

    import redis.asyncio as redis

    _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    pubsub = _redis_client.pubsub()
    channel = settings.redis_ws_channel
    await pubsub.psubscribe(f"{channel}*")
    _pubsub_task = asyncio.create_task(_listen(pubsub))
    logger.info("Redis WS: escuchando patron %s*", channel)


async def stop_ws_redis_bridge() -> None:
    global _redis_client, _pubsub_task

    if _pubsub_task:
        _pubsub_task.cancel()
        try:
            await _pubsub_task
        except asyncio.CancelledError:
            pass
        _pubsub_task = None

    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None


async def _listen(pubsub) -> None:
    from app.core.ws_manager import ws_manager

    try:
        async for message in pubsub.listen():
            if message["type"] not in ("message", "pmessage"):
                continue
            try:
                data = json.loads(message["data"])
                rooms: list[str] = data["rooms"]
                payload: dict[str, Any] = data["payload"]
            except (json.JSONDecodeError, KeyError, TypeError):
                continue

            for room in rooms:
                await ws_manager.broadcast_to_room(room, payload)
    except asyncio.CancelledError:
        await pubsub.punsubscribe(f"{settings.redis_ws_channel}*")
        await pubsub.aclose()
        raise


async def publish_ws_event(
    rooms: list[str],
    payload: dict[str, Any],
    tenant_slug: str | None = None,
) -> None:
    """Publica a Redis o entrega solo en este proceso si no hay Redis."""
    from app.core.ws_manager import ws_manager

    if not rooms:
        return

    if not redis_enabled():
        for room in rooms:
            await ws_manager.broadcast_to_room(room, payload)
        return

    if _redis_client is None:
        logger.warning("Redis WS: cliente no iniciado; entrega local")
        for room in rooms:
            await ws_manager.broadcast_to_room(room, payload)
        return

    await _redis_client.publish(
        resolve_ws_channel(tenant_slug),
        json.dumps({"rooms": rooms, "payload": payload}, default=str),
    )
