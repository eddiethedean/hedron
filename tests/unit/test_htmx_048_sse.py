"""SSE-048 SseRegion / SseTrigger over existing helpers."""

from __future__ import annotations

import pytest
from tests.unit._helpers_048 import injected_page

from hedron.experimental import job_status_sse_response, sse_response
from hedron.live_claims import EXPERIMENTAL_LIVE_SURFACES
from hedron_core import HedronError
from hedron_core.builtins import Page, Text
from hedron_core.codes import HED_EXT_0010
from hedron_core.live import SseEvent, encode_sse
from hedron_core.rendering import RenderMode, render
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.sse_ext import SseRegion, SseTrigger, parse_last_event_id


def test_sse_region_registers_and_emits_closed_tokens() -> None:
    region = SseRegion(
        Text("payload"),
        connect=SafeUrl.parse("/jobs/1/events", purpose=UrlPurpose.NAVIGATION),
        swap="job-status",
        close="hedron-close",
        id="live",
    )
    html, result = injected_page(region, htmx_extensions={"sse"}, title="Live")
    assert "sse.js" in html
    assert 'hx-ext="sse"' in html
    assert "sse-connect=" in html
    assert "sse-swap=" in html
    assert "job-status" in html
    assert result.htmx_plan.ids == ("sse",)  # type: ignore[union-attr]


def test_invalid_event_and_last_event_id() -> None:
    with pytest.raises(HedronError) as swap:
        SseRegion(Text("x"), connect="/events", swap="bad token")
    assert swap.value.diagnostic.code == HED_EXT_0010
    assert parse_last_event_id("evt-1") == "evt-1"
    with pytest.raises(HedronError) as last:
        parse_last_event_id("no\npe")
    assert last.value.diagnostic.code == HED_EXT_0010


def test_sse_trigger_and_existing_helpers_remain_experimental() -> None:
    trigger = SseTrigger(
        Text("panel"),
        event="job-status",
        href=SafeUrl.parse("/panel", purpose=UrlPurpose.NAVIGATION),
        target="#panel",
    )
    html = render(trigger, mode=RenderMode.FRAGMENT).html
    assert 'hx-trigger="sse:job-status"' in html
    frame = encode_sse(SseEvent(data="ok", event="job-status", id="1"))
    assert "event: job-status" in frame
    assert "sse_response" in EXPERIMENTAL_LIVE_SURFACES
    assert "job_status_sse_response" in EXPERIMENTAL_LIVE_SURFACES
    assert callable(sse_response)
    assert callable(job_status_sse_response)


def test_fragment_does_not_inject_sse_asset() -> None:
    region = SseRegion(Text("x"), connect="/events")
    html = render(Page(region, title="f"), mode=RenderMode.FRAGMENT).html
    assert "sse.js" not in html
