"""BROWSER-037: data-hx parity and rejection in hedron_core.html."""

from __future__ import annotations

import pytest

from hedron_core import html as h
from hedron_core.diagnostics import HedronError
from hedron_core.rendering import render
from hedron_core.security import SafeUrl, UrlPurpose


def test_data_hx_get_relative_path_renders() -> None:
    markup = render(h.button("Go", **{"data-hx-get": "/panel"})).html
    assert 'data-hx-get="/panel"' in markup or 'hx-get="/panel"' in markup


def test_data_hx_post_requires_safe_url_for_absolute() -> None:
    with pytest.raises(HedronError) as exc:
        render(h.button("Go", **{"data-hx-post": "https://evil.example/x"}))
    assert exc.value.diagnostic.code == "HED-SEC-0003"


def test_data_hx_post_accepts_safe_url() -> None:
    url = SafeUrl.parse("/run", purpose=UrlPurpose.NAVIGATION)
    markup = render(h.button("Go", **{"data-hx-post": url})).html
    assert 'hx-post="/run"' in markup or 'data-hx-post="/run"' in markup


def test_data_hx_rejects_javascript_scheme() -> None:
    with pytest.raises(HedronError):
        render(h.a("x", **{"data-hx-get": "javascript:alert(1)"}))
