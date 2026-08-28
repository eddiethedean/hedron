"""FastAPI page/session WebSocket channel helpers (phase 0.10)."""

from __future__ import annotations

import asyncio
import contextlib
import json
from collections.abc import Awaitable, Callable
from typing import Any

from starlette.websockets import WebSocket, WebSocketDisconnect

from hedron_core.channel import ChannelMessage, PageSessionChannel, RegionUpdate
from hedron_core.origin import is_same_origin

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
    return is_same_origin(
        origin,
        request_scheme=websocket.url.scheme or "http",
        request_hostname=websocket.url.hostname,
        request_port=websocket.url.port,
    )


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
    message_count = 0

    async def receive_with_lifecycle() -> str:
        """Race client input against a background producer failure."""
        if producer_task is None or producer_task.done():
            if producer_task is not None and not producer_task.cancelled():
                producer_error = producer_task.exception()
                if producer_error is not None:
                    raise producer_error
            return await asyncio.wait_for(
                websocket.receive_text(),
                timeout=channel.budget.idle_timeout_seconds,
            )

        receive_task = asyncio.create_task(websocket.receive_text())
        done, _pending = await asyncio.wait(
            {receive_task, producer_task},
            timeout=channel.budget.idle_timeout_seconds,
            return_when=asyncio.FIRST_COMPLETED,
        )
        if not done:
            receive_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await receive_task
            raise TimeoutError
        if producer_task in done:
            if producer_task.cancelled():
                receive_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await receive_task
                raise asyncio.CancelledError
            producer_error = producer_task.exception()
            if producer_error is not None:
                receive_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await receive_task
                raise producer_error
            # A normally completed producer does not close the client channel;
            # continue waiting for client frames under the ordinary idle bound.
            return await asyncio.wait_for(
                receive_task,
                timeout=channel.budget.idle_timeout_seconds,
            )
        return await receive_task

    try:
        if producer is not None:
            run_producer = producer

            async def _run_producer() -> None:
                await run_producer(channel, websocket)

            producer_task = asyncio.create_task(_run_producer())
            # Yield so a concurrent producer can start before a fast receive loop exits.
            await asyncio.sleep(0)
        while True:
            try:
                raw = await receive_with_lifecycle()
            except asyncio.TimeoutError:
                await websocket.send_text(json.dumps({"kind": "error", "detail": "idle timeout"}))
                await websocket.close(code=1008)
                return
            message_count += 1
            if message_count > channel.budget.max_messages:
                await websocket.send_text(
                    json.dumps({"kind": "error", "detail": "message budget exceeded"})
                )
                await websocket.close(code=1009)
                return
            if len(raw.encode("utf-8")) > channel.budget.max_message_bytes:
                await websocket.send_text(
                    json.dumps({"kind": "error", "detail": "message too large"})
                )
                await websocket.close(code=1009)
                return
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"kind": "error", "detail": "invalid json"}))
                await websocket.close(code=1003)
                return
            if not isinstance(data, dict):
                await websocket.send_text(
                    json.dumps({"kind": "error", "detail": "invalid json message"})
                )
                await websocket.close(code=1003)
                return
            kind = str(data.get("kind", ""))
            if kind == "close":
                break
            if kind == "client-state-request":
                component_id = str(data.get("component_id", ""))
                field = str(data.get("field", ""))
                try:
                    channel.validate_client_read(component_id, field)
                except ValueError as exc:
                    await websocket.send_text(json.dumps({"kind": "error", "detail": str(exc)}))
                    await websocket.close(code=1008)
                    return
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
            if not producer_task.done():
                producer_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
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
