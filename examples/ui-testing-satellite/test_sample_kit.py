"""Exercise an explicitly loaded specialist package contribution."""

from __future__ import annotations

import os

import pytest
from playwright.sync_api import expect

from hedron.testing.browser_scenario import BrowserScenarioFactory

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(
        os.environ.get("HEDRON_BROWSER") != "1",
        reason="Opt-in browser evidence: set HEDRON_BROWSER=1 and install a Playwright browser",
    ),
    pytest.mark.hedron_ui_contribution("hedron_sample_kit.ui_testing:CONTRIBUTION"),
]


def test_sample_kit_contribution(
    hedron_ui: BrowserScenarioFactory,
    sample_kit_app_factory: str,
) -> None:
    assert hedron_ui.contributions == (
        {
            "schema_version": 1,
            "package_id": "hedron-sample-kit",
            "package_version": "0.2.6",
            "hedron_version_range": ">=1.3,<2",
            "capabilities": ["sample_component_app"],
            "fixture_resources": ["sample_kit_app_factory"],
        },
    )
    with hedron_ui.from_app(
        sample_kit_app_factory,
        config={"message": "Loaded from the sample kit"},
    ) as ui:
        ui.page.goto(ui.url)
        expect(ui.region("sample-kit-region")).to_contain_text("Loaded from the sample kit")
