"""FastAPI page/session WebSocket channel helpers (phase 0.10)."""

from __future__ import annotations

import contextlib
import json
from collections.abc import Awaitable, Callable
from typing import Any
from urllib.parse import urlparse

from starlette.websockets import WebSocket, WebSocketDisconnect

from hedron_core.channel import ChannelMessage, PageSessionChannel, RegionUpdate

__all__ = [
    "accept_page_session_channel",
    "origin_allowed",
    "send_region_update",
]


def origin_allowed(websocket: WebSocket, *, allowed_origins: frozenset[str] | None = None) -> bool:
    origin = websocket.headers.get("origin")
    if origin is None:
        return True
    if allowed_origins is not None:
        return origin in allowed_origins
    # Default: same-origin with the request URL host.
    host = websocket.url.hostname
    parsed = urlparse(origin)
    return bool(host) and parsed.hostname == host


async def accept_page_session_channel(
    websocket: WebSocket,
    channel: PageSessionChannel,
    *,
    allowed_origins: frozenset[str] | None = None,
    on_client_state: Callable[[str, str], Awaitable[Any]] | None = None,
    producer: Callable[[PageSessionChannel, WebSocket], Awaitable[None]] | None = None,
) -> None:
    if not origin_allowed(websocket, allowed_origins=allowed_origins):
        await websocket.close(code=1008)
        return
    await websocket.accept()
    try:
        if producer is not None:
            await producer(channel, websocket)
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            kind = str(data.get("kind", ""))
            if kind == "close":
                break
            if kind == "client-state-request":
                component_id = str(data.get("component_id", ""))
                field = str(data.get("field", ""))
                channel.validate_client_read(component_id, field)
                value = None
                if on_client_state is not None:
                    value = await on_client_state(component_id, field)
                await websocket.send_text(
                    json.dumps(
                        {
                            "kind": "client-state",
                            "component_id": component_id,
                            "field": field,
                            "value": value,
                        }
                    )
                )
            elif kind == "ping":
                await websocket.send_text(json.dumps({"kind": "ping"}))
    except WebSocketDisconnect:
        return
    finally:
        with contextlib.suppress(Exception):
            await websocket.close()


async def send_region_update(
    websocket: WebSocket,
    channel: PageSessionChannel,
    update: RegionUpdate,
) -> None:
    message: ChannelMessage = channel.encode_region_update(update)
    await websocket.send_text(json.dumps({"kind": message.kind, **dict(message.payload)}))
