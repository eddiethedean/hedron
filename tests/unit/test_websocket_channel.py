"""WebSocket channel contract tests."""

from __future__ import annotations

import pytest

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
    from hedron.websocket_channel import origin_allowed

    class _WS:
        def __init__(self) -> None:
            self.headers = {"origin": "https://example.com"}
            self.url = type("U", (), {"hostname": "example.com"})()

    ws = _WS()
    assert origin_allowed(ws) is True  # type: ignore[arg-type]
    assert origin_allowed(ws, allowed_origins=frozenset({"https://other.test"})) is False  # type: ignore[arg-type]
