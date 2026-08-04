"""WebSocket channel contract tests."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from hedron.websocket_channel import (
    ALLOW_MISSING_ORIGIN,
    accept_page_session_channel,
    origin_allowed,
    send_region_update,
)
from hedron_core.channel import ClientStateRead, PageSessionChannel, RegionUpdate


def test_page_session_channel_declared_regions() -> None:
    channel = PageSessionChannel(
        channel_id="c1",
        declared_regions=frozenset({"status", "list"}),
        declared_client_reads=(ClientStateRead("form", "q"),),
        fallback="poll",
    )
    msg = channel.encode_region_update(RegionUpdate(region_id="status", html="<b>ok</b>"))
    assert msg.kind == "region-update"
    assert msg.payload["region_id"] == "status"

    with pytest.raises(ValueError, match="undeclared region"):
        channel.encode_region_update(RegionUpdate(region_id="other", html="x"))

    channel.validate_client_read("form", "q")
    with pytest.raises(ValueError, match="undeclared client read"):
        channel.validate_client_read("form", "secret")


def test_origin_allowed_helper() -> None:
    class _WS:
        def __init__(self, origin: str | None = "https://example.com") -> None:
            self.headers = {} if origin is None else {"origin": origin}
            self.url = type("U", (), {"hostname": "example.com"})()

    ws = _WS()
    assert origin_allowed(ws) is True  # type: ignore[arg-type]
    assert origin_allowed(ws, allowed_origins=frozenset({"https://other.test"})) is False  # type: ignore[arg-type]
    assert origin_allowed(_WS(origin=None)) is False  # type: ignore[arg-type]
    assert origin_allowed(_WS(origin=None), allow_missing_origin=True) is True  # type: ignore[arg-type]
    assert (
        origin_allowed(_WS(origin=None), allowed_origins=frozenset({ALLOW_MISSING_ORIGIN})) is True  # type: ignore[arg-type]
    )


def test_accept_replies_pong_and_runs_producer_concurrently() -> None:
    channel = PageSessionChannel(
        channel_id="c1",
        declared_regions=frozenset({"status"}),
        declared_client_reads=(),
    )
    websocket = MagicMock()
    websocket.headers = {"origin": "https://example.com"}
    websocket.url = type("U", (), {"hostname": "example.com"})()
    websocket.accept = AsyncMock()
    websocket.close = AsyncMock()
    websocket.send_text = AsyncMock()

    messages = [
        json.dumps({"kind": "ping"}),
        json.dumps({"kind": "close"}),
    ]
    websocket.receive_text = AsyncMock(side_effect=messages)

    async def _run() -> None:
        producer_started = asyncio.Event()

        async def producer(_channel: PageSessionChannel, _ws: object) -> None:
            producer_started.set()
            await asyncio.Event().wait()

        task = asyncio.create_task(
            accept_page_session_channel(websocket, channel, producer=producer)  # type: ignore[arg-type]
        )
        await asyncio.wait_for(producer_started.wait(), timeout=1.0)
        await asyncio.wait_for(task, timeout=2.0)
        assert producer_started.is_set()

    asyncio.run(_run())
    sent = [json.loads(call.args[0]) for call in websocket.send_text.await_args_list]
    assert {"kind": "pong"} in sent


def test_send_region_update_encodes_payload() -> None:
    channel = PageSessionChannel(
        channel_id="c1",
        declared_regions=frozenset({"status"}),
        declared_client_reads=(),
    )
    websocket = MagicMock()
    websocket.send_text = AsyncMock()

    async def _run() -> None:
        await send_region_update(
            websocket,  # type: ignore[arg-type]
            channel,
            RegionUpdate(region_id="status", html="<b>ok</b>"),
        )

    asyncio.run(_run())
    payload = json.loads(websocket.send_text.await_args.args[0])
    assert payload["kind"] == "region-update"
    assert payload["region_id"] == "status"
