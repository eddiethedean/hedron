"""HTMX-037: SafeUrl enforcement on action-async hx-post."""

from __future__ import annotations

import pytest

from hedron_core.diagnostics import HedronError
from hedron_core.rendering import render
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_elements.action_async import ActionAsync


def test_action_async_accepts_safe_relative_hx_post() -> None:
    html = render(
        ActionAsync("Submit", hx_post=SafeUrl.parse("/api/run", purpose=UrlPurpose.NAVIGATION))
    ).html
    assert 'hx-post="/api/run"' in html


def test_action_async_rejects_raw_absolute_url_string() -> None:
    with pytest.raises(HedronError):
        ActionAsync("Submit", hx_post="https://evil.example/run")


def test_action_async_markup_rejects_unsafe_hx_post() -> None:
    with pytest.raises(HedronError) as exc:
        ActionAsync("Submit", hx_post="javascript:alert(1)").render_markup()
    assert exc.value.diagnostic.code in {"HED-SEC-0001", "HED-SEC-0003", "HED-HTML-0005"}
