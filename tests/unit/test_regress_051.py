"""REGRESS-051 fleet integrity and companion authoring."""

from __future__ import annotations

from pathlib import Path

from hedron.testing import assert_renders
from hedron_core.builtins import BusyRegion, SwapReveal, TextInput
from hedron_core.htmx.attrs import Hx


def test_password_toggle_and_busy_reveal() -> None:
    html = assert_renders(
        TextInput("secret", type="password"),
        contains="hedron-password-field",
    )
    assert 'type="password"' in html
    assert "data-hedron-password-toggle" in html
    assert "Show password" in html
    reveal = assert_renders(SwapReveal("hello"), contains="data-hedron-reveal")
    assert "respect" in reveal
    assert "is-revealed" in reveal
    busy = assert_renders(BusyRegion("body"), contains='aria-busy="false"')
    assert "data-hedron-busy" in busy
    attrs = Hx(method="post", url="/x", busy="region", indicator="#busy").as_html_attrs()
    assert attrs["data-hedron-busy"] == "region"
    assert attrs["aria-busy"] == "false"
    assert attrs["data-hedron-busy-indicator"] == "#busy"
    assert attrs["hx-indicator"] == "#busy"


def test_050_packet_remains() -> None:
    assert Path("docs/acceptance/release-gate-0.50.toml").is_file()
    assert Path("scripts/verify_pkg_50.py").is_file()
    ui_path = Path("packages/hedron-core/src/hedron_core/static/hedron-ui.mjs")
    ui = ui_path.read_text(encoding="utf-8")
    assert "data-hedron-password-toggle" in ui
    assert "prefers-reduced-motion" in ui
    assert "htmx:beforeRequest" in ui
    assert "busyCounts" in ui


def test_send_error_handler_clears_busy() -> None:
    for rel in (
        "packages/hedron-core/src/hedron_core/static/hedron-ui.mjs",
        "packages/hedron/src/hedron/static/hedron-ui.mjs",
    ):
        ui = Path(rel).read_text(encoding="utf-8")
        for event in ("htmx:sendError", "htmx:responseError"):
            idx = ui.index(event)
            block = ui[idx : idx + 400]
            assert "setBusy" in block, f"{rel} {event} must clear busy"
            assert "false" in block, f"{rel} {event} must decrement busy"
