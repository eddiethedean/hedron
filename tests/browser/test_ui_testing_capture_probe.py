"""Synthetic-only capture exercise used to freeze native trace storage limits."""

from __future__ import annotations

import os

import pytest
from playwright.sync_api import expect

from hedron.testing.browser_scenario import BrowserScenarioFactory

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(
        os.environ.get("HEDRON_BROWSER") != "1",
        reason="Opt-in Linux browser evidence: set HEDRON_BROWSER=1",
    ),
    pytest.mark.skipif(
        os.environ.get("HEDRON_UI_CAPTURE_PROBE_FAIL") != "1",
        reason="synthetic trace budget probe is isolated to the failure-capture lane",
    ),
]


@pytest.mark.hedron_capture(profile="synthetic", data="synthetic")
def test_synthetic_trace_capture_probe(hedron_ui: BrowserScenarioFactory) -> None:
    with hedron_ui.from_app(
        "hedron.testing.examples.profile_app:create_app",
        config={"title": "Synthetic capture probe"},
        synthetic=True,
    ) as ui:
        ui.page.goto(ui.url)
        expect(ui.page.get_by_role("heading", name="Synthetic capture probe")).to_be_visible()
        if os.environ.get("HEDRON_UI_CAPTURE_PROBE_FAIL") == "1":
            pytest.fail("intentional synthetic capture budget probe")
