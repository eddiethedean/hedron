"""FastAPI page/session WebSocket channel helpers (phase 0.10)."""

from __future__ import annotations

import asyncio
import contextlib
import json
from collections.abc import Awaitable, Callable
from typing import Any
from urllib.parse import urlparse

from starlette.websockets import WebSocket, WebSocketDisconnect

from hedron_core.channel import ChannelMessage, PageSessionChannel, RegionUpdate

__all__ = [
    "ALLOW_MISSING_ORIGIN",
    "accept_page_session_channel",
    "origin_allowed",
    "send_region_update",
]

# Include this sentinel in ``allowed_origins`` to permit connections with no Origin header.
ALLOW_MISSING_ORIGIN = "*"


def origin_allowed(
    websocket: WebSocket,
    *,
    allowed_origins: frozenset[str] | None = None,
    allow_missing_origin: bool = False,
) -> bool:
    """Return whether the WebSocket Origin is permitted.

    Missing Origin is denied by default (same-origin policy). Pass
    ``allow_missing_origin=True`` or include :data:`ALLOW_MISSING_ORIGIN` in
    ``allowed_origins`` for non-browser clients.
    """
    origin = websocket.headers.get("origin")
    if origin is None:
        if allow_missing_origin:
            return True
        return bool(allowed_origins is not None and ALLOW_MISSING_ORIGIN in allowed_origins)
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
    allow_missing_origin: bool = False,
    on_client_state: Callable[[str, str], Awaitable[Any]] | None = None,
    producer: Callable[[PageSessionChannel, WebSocket], Awaitable[None]] | None = None,
) -> None:
    if not origin_allowed(
        websocket,
        allowed_origins=allowed_origins,
        allow_missing_origin=allow_missing_origin,
    ):
        await websocket.close(code=1008)
        return
    await websocket.accept()
    producer_task: asyncio.Task[None] | None = None
    try:
        if producer is not None:
            run_producer = producer

            async def _run_producer() -> None:
                await run_producer(channel, websocket)

            producer_task = asyncio.create_task(_run_producer())
            # Yield so a concurrent producer can start before a fast receive loop exits.
            await asyncio.sleep(0)
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
                await websocket.send_text(json.dumps({"kind": "pong"}))
    except WebSocketDisconnect:
        return
    finally:
        if producer_task is not None:
            producer_task.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await producer_task
        with contextlib.suppress(Exception):
            await websocket.close()


async def send_region_update(
    websocket: WebSocket,
    channel: PageSessionChannel,
    update: RegionUpdate,
) -> None:
    message: ChannelMessage = channel.encode_region_update(update)
    await websocket.send_text(json.dumps({"kind": message.kind, **dict(message.payload)}))
