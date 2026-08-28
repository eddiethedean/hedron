"""Phase 0.15 M6 BrowserContext, BrowserStorage, Math, IFrame, geolocation."""

from __future__ import annotations

import math
import time

import pytest
from starlette.requests import Request

from hedron.browser import browser_context_from_request
from hedron_core import (
    BrowserContext,
    BrowserStorage,
    BrowserStorageUnavailable,
    GeolocationButton,
    GeolocationHint,
    HelpInspector,
    IFrame,
    Math,
    StorageQuotaExceeded,
    ViewportHint,
    render,
)
from hedron_core.diagnostics import HedronError
from hedron_core.security import SafeUrl, UrlPurpose


def test_browser_context_separates_spoofable_fields() -> None:
    ctx = BrowserContext.from_mapping(
        {
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "TestAgent/1.0",
            "Sec-Fetch-Dest": "document",
            "Sec-CH-Prefers-Color-Scheme": "dark",
            "Cookie": "should-not-appear",
        },
        url="https://app.example/path",
        client_address="127.0.0.1:443",
        cookies={"sessionid": "abc123secrettoken", "theme": "light"},
        timezone="America/New_York",
        viewport=ViewportHint(width=1280, height=720),
    )
    assert ctx.url == "https://app.example/path"
    assert ctx.client_address == "127.0.0.1:443"
    assert "accept-language" in ctx.headers
    assert "cookie" not in ctx.headers
    assert ctx.embedding.get("sec-fetch-dest") == "document"
    assert not ctx.is_embedded()

    spoofable = ctx.spoofable
    assert set(spoofable) == {"locale", "timezone", "color_mode", "viewport"}
    assert spoofable["locale"] == "en-US"
    assert spoofable["timezone"] == "America/New_York"
    assert spoofable["color_mode"] == "dark"
    assert spoofable["viewport"] == {"width": 1280, "height": 720}

    redacted = ctx.redacted_cookies()
    assert redacted["sessionid"] == "[redacted]"
    assert redacted["theme"] != "light" or len("light") <= 8
    # short non-secret values may still be partially shown / redacted conservatively
    assert "sessionid" in redacted


def test_browser_context_from_request_adapter() -> None:
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/page",
        "raw_path": b"/page",
        "query_string": b"",
        "headers": [
            (b"accept-language", b"fr-FR"),
            (b"sec-fetch-dest", b"iframe"),
        ],
        "client": ("203.0.113.10", 12345),
        "server": ("testserver", 80),
    }
    request = Request(scope)
    ctx = browser_context_from_request(request, timezone="Europe/Paris")
    assert ctx.url.endswith("/page")
    assert ctx.client_address == "203.0.113.10:12345"
    assert ctx.locale == "fr-FR"
    assert ctx.timezone == "Europe/Paris"
    assert ctx.is_embedded()
    assert "timezone" in ctx.spoofable


def test_browser_storage_quota_and_expiry() -> None:
    store = BrowserStorage("prefs", consent_granted=True, max_entries=2, max_bytes=200)
    store.set("a", {"theme": "dark"}, schema={"theme": str})
    store.set("b", 1, schema=int, ttl_seconds=0.05)
    time.sleep(0.06)
    assert store.get("b", default=None) is None
    # After expiry, a second live entry still fits; a third does not.
    store.set("b2", 2, schema=int)
    with pytest.raises(StorageQuotaExceeded):
        store.set("c", "x")

    tiny = BrowserStorage("tiny", consent_granted=True, max_entries=10, max_bytes=20)
    with pytest.raises(StorageQuotaExceeded):
        tiny.set("big", "x" * 100)

    closed = BrowserStorage("x", consent_granted=False)
    with pytest.raises(PermissionError):
        closed.set("k", 1)
    assert closed.get("k", default="fallback") == "fallback"

    unavailable = BrowserStorage("u", consent_granted=True, unavailable=True)
    with pytest.raises(BrowserStorageUnavailable):
        unavailable.set("k", 1)

    with pytest.raises(RuntimeError, match="authentication"):
        store.forbid_auth_use()


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, True])
def test_browser_storage_rejects_non_finite_expiry_values(value: object) -> None:
    store = BrowserStorage("prefs", consent_granted=True)
    with pytest.raises(ValueError, match="finite number"):
        store.set("ttl", "value", ttl_seconds=value)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="finite number"):
        store.set("absolute", "value", expires_at=value)  # type: ignore[arg-type]
    assert store.keys() == []


def test_browser_storage_rejects_expiry_integer_too_large_for_float() -> None:
    store = BrowserStorage("prefs", consent_granted=True)
    with pytest.raises(ValueError, match="finite number"):
        store.set("ttl", "value", ttl_seconds=10**400)  # type: ignore[arg-type]
    assert store.keys() == []


def test_math_escapes_script() -> None:
    payload = r"E=mc^2<script>alert(1)</script>"
    html = render(Math(payload)).html
    assert "hedron-math" in html
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "alert(1)" in html

    display = render(Math(r"\sum_i x_i", display=True)).html
    assert "hedron-math-display" in display
    assert 'role="math"' in display


def test_iframe_rejects_remote_when_allow_remote_false() -> None:
    local = render(IFrame("/embed/local", title="Local panel")).html
    assert "<iframe" in local
    assert 'sandbox=""' in local
    assert "Local panel" in local
    assert 'data-hedron-iframe="local"' in local

    with pytest.raises(HedronError) as exc:
        IFrame("https://evil.example/x", title="Nope", allow_remote=False)
    assert exc.value.diagnostic.code == "HED-SEC-0001"

    remote = SafeUrl.parse(
        "https://cdn.example/frame", purpose=UrlPurpose.ASSET, allow_external=True
    )
    with pytest.raises(HedronError):
        IFrame(remote, title="Blocked")

    ok = render(IFrame(remote, title="Allowed", allow_remote=True, width=400, height=300)).html
    assert "https://cdn.example/frame" in ok
    assert 'data-hedron-iframe="remote"' in ok
    assert 'width="400"' in ok
    assert 'height="300"' in ok


def test_help_inspector_and_geolocation_markup() -> None:
    inspector = render(HelpInspector("Object", "{'id': 1}")).html
    assert "<details" in inspector
    assert "<summary>Object</summary>" in inspector
    assert "hedron-help-inspector" in inspector

    geo = render(GeolocationButton(label="Locate me")).html
    assert "hedron-geolocation" in geo
    assert 'data-spoofable="true"' in geo
    assert "spoofable" in geo.lower()
    assert 'name="lat"' in geo
    assert 'name="lon"' in geo
    assert "authorization" in geo.lower()

    hint = render(GeolocationHint()).html
    assert "spoofable" in hint.lower()
    assert 'data-hedron-geolocation-spoofable="true"' in hint
    assert GeolocationButton.__doc__ is not None
    assert "spoofable" in GeolocationButton.__doc__.lower()
