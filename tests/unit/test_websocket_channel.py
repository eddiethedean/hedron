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
from hedron_core.channel import ChannelBudget, ClientStateRead, PageSessionChannel, RegionUpdate


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
        def __init__(
            self,
            origin: str | None = "https://example.com",
            *,
            hostname: str = "example.com",
            scheme: str = "wss",
            port: int | None = None,
        ) -> None:
            self.headers = {} if origin is None else {"origin": origin}
            self.url = type(
                "U",
                (),
                {"hostname": hostname, "scheme": scheme, "port": port},
            )()

    ws = _WS()
    assert origin_allowed(ws) is True  # type: ignore[arg-type]
    assert origin_allowed(ws, allowed_origins=frozenset({"https://other.test"})) is False  # type: ignore[arg-type]
    assert origin_allowed(_WS(origin=None)) is False  # type: ignore[arg-type]
    assert origin_allowed(_WS(origin=None), allow_missing_origin=True) is True  # type: ignore[arg-type]
    assert (
        origin_allowed(_WS(origin=None), allowed_origins=frozenset({ALLOW_MISSING_ORIGIN})) is True  # type: ignore[arg-type]
    )
    # Different ports are different origins.
    assert (
        origin_allowed(
            _WS(origin="https://example.com:8443", scheme="wss", port=443)  # type: ignore[arg-type]
        )
        is False
    )
    assert (
        origin_allowed(
            _WS(origin="https://example.com:8443", scheme="wss", port=8443)  # type: ignore[arg-type]
        )
        is True
    )
    # Scheme mismatch (http Origin vs wss upgrade).
    assert origin_allowed(_WS(origin="http://example.com", scheme="wss")) is False  # type: ignore[arg-type]


def test_accept_replies_pong_and_runs_producer_concurrently() -> None:
    channel = PageSessionChannel(
        channel_id="c1",
        declared_regions=frozenset({"status"}),
        declared_client_reads=(),
    )
    websocket = MagicMock()
    websocket.headers = {"origin": "https://example.com"}
    websocket.url = type("U", (), {"hostname": "example.com", "scheme": "wss", "port": None})()
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


def test_issue_98_rejects_non_object_json_frames() -> None:
    """#98: scalar JSON frames must not crash the channel loop."""
    channel = PageSessionChannel(
        channel_id="c1",
        declared_regions=frozenset({"status"}),
        declared_client_reads=(),
    )
    websocket = MagicMock()
    websocket.headers = {"origin": "https://example.com"}
    websocket.url = type("U", (), {"hostname": "example.com", "scheme": "wss", "port": None})()
    websocket.accept = AsyncMock()
    websocket.close = AsyncMock()
    websocket.send_text = AsyncMock()
    websocket.receive_text = AsyncMock(side_effect=[json.dumps(["not", "an", "object"])])

    async def _run() -> None:
        await accept_page_session_channel(websocket, channel)  # type: ignore[arg-type]

    asyncio.run(_run())
    websocket.close.assert_awaited()
    sent = [json.loads(call.args[0]) for call in websocket.send_text.await_args_list]
    assert any(msg.get("detail") == "invalid json message" for msg in sent)


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


def test_send_region_update_rejects_oversized_wire_frame() -> None:
    channel = PageSessionChannel(
        channel_id="c1",
        declared_regions=frozenset({"status"}),
        budget=ChannelBudget(max_message_bytes=10),
    )
    websocket = MagicMock()
    websocket.send_text = AsyncMock()

    async def _run() -> None:
        await send_region_update(
            websocket,  # type: ignore[arg-type]
            channel,
            RegionUpdate(region_id="status", html="x"),
        )

    with pytest.raises(ValueError, match="outbound message exceeds max_message_bytes"):
        asyncio.run(_run())
    websocket.send_text.assert_not_awaited()
    assert channel.messages_sent == 0


def test_client_state_response_rejects_oversized_wire_frame() -> None:
    channel = PageSessionChannel(
        channel_id="c1",
        declared_regions=frozenset(),
        declared_client_reads=(ClientStateRead("form", "value"),),
        budget=ChannelBudget(max_message_bytes=100),
    )
    websocket = MagicMock()
    websocket.headers = {"origin": "https://example.com"}
    websocket.url = type("U", (), {"hostname": "example.com", "scheme": "wss", "port": None})()
    websocket.accept = AsyncMock()
    websocket.close = AsyncMock()
    websocket.send_text = AsyncMock()
    websocket.receive_text = AsyncMock(
        return_value=json.dumps(
            {"kind": "client-state-request", "component_id": "form", "field": "value"}
        )
    )

    async def _state(_component_id: str, _field: str) -> str:
        return "x" * 200

    async def _run() -> None:
        await accept_page_session_channel(
            websocket,  # type: ignore[arg-type]
            channel,
            on_client_state=_state,
        )

    asyncio.run(_run())
    websocket.send_text.assert_not_awaited()
    websocket.close.assert_any_await(code=1009)


def test_oversized_error_frame_does_not_close_twice() -> None:
    class _StrictWebSocket:
        def __init__(self) -> None:
            self.headers = {"origin": "https://example.com"}
            self.url = type("U", (), {"hostname": "example.com", "scheme": "wss", "port": None})()
            self.closed = False
            self.close_codes: list[int] = []
            self.sent: list[str] = []

        async def accept(self) -> None:
            return None

        async def receive_text(self) -> str:
            return "x"

        async def send_text(self, text: str) -> None:
            if self.closed:
                raise RuntimeError("cannot send after close")
            self.sent.append(text)

        async def close(self, code: int = 1000) -> None:
            if self.closed:
                raise RuntimeError("cannot close twice")
            self.closed = True
            self.close_codes.append(code)

    websocket = _StrictWebSocket()
    channel = PageSessionChannel(
        channel_id="c1",
        declared_regions=frozenset(),
        budget=ChannelBudget(max_message_bytes=10),
    )

    asyncio.run(
        accept_page_session_channel(websocket, channel)  # type: ignore[arg-type]
    )

    assert websocket.close_codes == [1009]
    assert websocket.sent == []


def test_client_state_serialization_error_is_not_reported_as_oversized() -> None:
    channel = PageSessionChannel(
        channel_id="c1",
        declared_regions=frozenset(),
        declared_client_reads=(ClientStateRead("form", "value"),),
        budget=ChannelBudget(max_message_bytes=1_000),
    )
    websocket = MagicMock()
    websocket.headers = {"origin": "https://example.com"}
    websocket.url = type("U", (), {"hostname": "example.com", "scheme": "wss", "port": None})()
    websocket.accept = AsyncMock()
    websocket.close = AsyncMock()
    websocket.send_text = AsyncMock()
    websocket.receive_text = AsyncMock(
        return_value=json.dumps(
            {"kind": "client-state-request", "component_id": "form", "field": "value"}
        )
    )

    async def _state(_component_id: str, _field: str) -> dict[str, object]:
        value: dict[str, object] = {}
        value["self"] = value
        return value

    async def _run() -> None:
        await accept_page_session_channel(
            websocket,  # type: ignore[arg-type]
            channel,
            on_client_state=_state,
        )

    with pytest.raises(ValueError, match="Circular reference detected"):
        asyncio.run(_run())
    websocket.send_text.assert_not_awaited()
    assert all(call.kwargs.get("code") != 1009 for call in websocket.close.await_args_list)
