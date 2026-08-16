"""A11Y-043: native controls, host semantics, no-JS, zoom-safe markup."""

from __future__ import annotations

from tests.unit._helpers_043 import make_app, reset_043

from hedron import Form, Page, Text
from hedron_core.hosts import FragmentHost
from hedron_core.rendering import render


def setup_function() -> None:
    reset_043()


def test_host_is_semantic_neutral_by_default() -> None:
    host = FragmentHost(Text("panel"), dom_id="h-view-status")
    html = render(host).html
    assert html.startswith("<div") or "<div" in html
    assert 'role="main"' not in html
    assert 'aria-busy="false"' in html
    assert "<nav" not in html
    explicit = FragmentHost(Text("named"), tag="section", role="status", aria_live="polite")
    named = render(explicit).html
    assert "<section" in named
    assert 'role="status"' in named
    assert 'aria-live="polite"' in named


def test_native_button_and_form_no_custom_element() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("idle")

    @app.command(fallback="/status-page")
    def ping():
        return Text("pong")

    page = render(
        Page(
            status(),
            status.refresh_button("Refresh"),
            ping.button("Ping"),
            Form(action=ping),
            title="A11y",
        )
    ).html
    assert "<button" in page
    assert "<form" in page
    assert "hedron-refresh" not in page
    assert "<hedron-" not in page
    assert 'type="button"' in page or "type='button'" in page
    # No-JS: form/action fallback is an ordinary POST URL.
    assert ping.path in page
    assert "data-hedron-fallback" in page


def test_reduced_motion_forced_colors_zoom_do_not_require_custom_runtime() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("zoom")

    html = render(status()).html
    assert "width:" not in html
    assert "px;" not in html
    assert "vh" not in html
    # Keyboard: native button is in-tab-order; host is a static wrapper.
    assert 'tabindex="-1"' not in html
