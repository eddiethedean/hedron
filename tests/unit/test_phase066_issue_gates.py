"""Regression coverage for the remaining Hedron 0.66 issue gates."""

from __future__ import annotations

import asyncio
import io
import json
import math
import zipfile
from unittest.mock import AsyncMock

import pytest

from hedron.auth.flow import RateLimitPolicy
from hedron.auth.oidc import redact_claims
from hedron.cli.discovery import _next_minor_ceiling as discovery_next_minor
from hedron.migrate.pins import _next_minor_ceiling as migrate_next_minor
from hedron.security.auth_rate_limit import AuthRateLimiter
from hedron.websocket_channel import accept_page_session_channel
from hedron_core import render
from hedron_core.builtins.content import Heading, Text
from hedron_core.builtins.layout import PageHeader
from hedron_core.builtins.style_scope import StyleScope
from hedron_core.channel import PageSessionChannel
from hedron_core.diagnostics import HedronError
from hedron_core.htmx_contract import approved_headers
from hedron_core.theme_platform import load_theme_package
from hedron_data.memory import InMemoryDataSource
from hedron_data.sources import CellUpdate, DataChanges, DataQuery
from hedron_maps.spec import Bounds, ViewState


def test_memory_audit_failure_does_not_publish_candidate() -> None:
    def reject(_candidate: object) -> None:
        raise RuntimeError("audit unavailable")

    source = InMemoryDataSource(
        [{"id": "1", "name": "before"}],
        writable_fields=frozenset({"name"}),
        audit_hook=reject,
    )

    with pytest.raises(RuntimeError, match="audit unavailable"):
        source.apply(
            DataChanges(
                updates=(CellUpdate(row_key="1", field="name", value="after"),),
            )
        )
    assert source.fetch(DataQuery(limit=10)).rows[0]["name"] == "before"


def test_structured_headers_and_map_payloads_reject_nonfinite_values() -> None:
    with pytest.raises(ValueError):
        approved_headers(trigger={"nested": [math.nan]})
    with pytest.raises(ValueError):
        approved_headers(location={"path": "/ok", "values": {"x": math.inf}})
    with pytest.raises(ValueError):
        ViewState(center=(0.0, math.nan))
    with pytest.raises(ValueError):
        Bounds(west=0, south=0, east=math.inf, north=1)


def test_redact_claims_tolerates_malformed_raw_claim() -> None:
    result = redact_claims({"sub": "user", "raw": None})
    assert result["sub"] == "user"
    assert result["raw"] == {}
    result = redact_claims({"sub": "user", "raw": "not-a-mapping"})
    assert result["raw"] == {}


def test_theme_package_member_limits_are_checked_before_reads() -> None:
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr("manifest.json", b"{}")
        archive.writestr("manifest.json", b"{}")
        archive.writestr("theme.json", b"{}")
    with pytest.raises(ValueError, match="invalid theme package archive"):
        load_theme_package(payload.getvalue())


def test_release_pin_bounds_increment_minor_without_dropping_major() -> None:
    assert discovery_next_minor("1.2.3") == "1.3"
    assert migrate_next_minor("2.9.0") == "2.10"
    assert discovery_next_minor("0.66.1") == "0.67"


def test_rate_limit_windows_reject_nonfinite_values() -> None:
    for value in (math.nan, math.inf, -math.inf, True):
        with pytest.raises((ValueError, HedronError)):
            AuthRateLimiter(limit=1, window_seconds=value)  # type: ignore[arg-type]
        with pytest.raises((ValueError, HedronError)):
            RateLimitPolicy(limit=1, window_seconds=value)  # type: ignore[arg-type]


def test_websocket_producer_failure_is_propagated_immediately() -> None:
    channel = PageSessionChannel(channel_id="c1", declared_regions=frozenset({"status"}))
    websocket = type("WS", (), {})()
    websocket.headers = {"origin": "https://example.com"}
    websocket.url = type("U", (), {"hostname": "example.com", "scheme": "wss", "port": None})()

    async def _run() -> None:
        websocket.accept = AsyncMock()
        websocket.close = AsyncMock()
        websocket.send_text = AsyncMock()

        async def receive_text() -> str:
            await asyncio.sleep(10)
            return json.dumps({"kind": "close"})

        websocket.receive_text = receive_text

        async def producer(_channel: object, _ws: object) -> None:
            raise RuntimeError("producer failed")

        with pytest.raises(RuntimeError, match="producer failed"):
            await asyncio.wait_for(
                accept_page_session_channel(websocket, channel, producer=producer), timeout=1
            )

    asyncio.run(_run())


def test_typography_measure_effect_and_presentation_scope_are_bounded() -> None:
    assert 'data-hedron-type-measure="narrow"' in render(
        Heading("Title", measure="narrow", effect="subtle")
    ).html
    assert 'data-hedron-type-effect="display"' in render(
        Text("Body", effect="display")
    ).html
    rendered = render(
        PageHeader(
            "Title",
            description="Description",
            title_measure="wide",
            description_measure="narrow",
        )
    ).html
    assert rendered.count("data-hedron-type-measure") == 2
    scope = StyleScope(
        presentation={"PageHeader.title": "auth-display", "Card.heading": "workspace"}
    )
    assert scope.style_context.resolve_presentation("PageHeader.title") == "auth-display"
    assert "PageHeader.title=auth-display" in render(scope).html
    with pytest.raises((ValueError, HedronError)):
        StyleScope(presentation={"arbitrary .selector": "bad"})
