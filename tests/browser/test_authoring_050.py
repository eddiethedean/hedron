"""BROWSER authoring smoke for ToastHost / Hx validate (opt-in Playwright)."""

from __future__ import annotations

import os

import pytest

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(
        os.environ.get("HEDRON_BROWSER") != "1",
        reason="Opt-in: set HEDRON_BROWSER=1",
    ),
]


def test_hedron_ui_has_toast_and_error_listeners() -> None:
    from pathlib import Path

    ui = Path("packages/hedron-core/src/hedron_core/static/hedron-ui.mjs").read_text(
        encoding="utf-8"
    )
    assert "hedron-toast" in ui
    assert "htmx:responseError" in ui
