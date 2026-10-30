"""Deliberately fail with synthetic secrets to test structured-manifest privacy."""

from __future__ import annotations

import os
from urllib.parse import parse_qs, urlsplit

import pytest

from hedron.testing.browser_scenario import BrowserScenarioFactory

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(
        os.environ.get("HEDRON_BROWSER") != "1",
        reason="Opt-in Linux browser evidence: set HEDRON_BROWSER=1",
    ),
    pytest.mark.skipif(
        os.environ.get("HEDRON_UI_CANARY_PROBE") != "1",
        reason="structured privacy canary is isolated to the privacy-probe lane",
    ),
]


def test_structured_failure_manifest_omits_confidential_canaries(
    hedron_ui: BrowserScenarioFactory,
) -> None:
    secret = os.environ["HEDRON_UI_CANARY_SECRET"]
    values = {
        "form": f"{secret}_form",
        "query": f"{secret}_query",
        "header": f"{secret}_header",
        "cookie": f"{secret}_cookie",
        "storage": f"{secret}_storage",
        "console": f"{secret}_console",
        "exception": f"{secret}_exception",
        "target": f"{secret}_target",
        "path": f"{secret}_path",
    }

    with hedron_ui.from_app(
        "hedron.testing.examples.profile_app:create_app",
        config={"title": "Synthetic privacy canary"},
    ) as ui:
        ui.context.add_cookies(
            [{"name": "private-canary", "value": values["cookie"], "url": ui.url}]
        )
        observed_headers: list[str] = []
        observed_console: list[str] = []
        ui.page.on(
            "request",
            lambda request: observed_headers.append(
                request.headers.get("x-hedron-private-canary", "")
            ),
        )
        ui.page.on("console", lambda message: observed_console.append(message.text))
        ui.page.set_extra_http_headers({"X-Hedron-Private-Canary": values["header"]})
        ui.page.goto(f"{ui.url}?private={values['query']}")
        assert parse_qs(urlsplit(ui.page.url).query)["private"] == [values["query"]]
        assert any(value == values["header"] for value in observed_headers)
        assert any(cookie.get("value") == values["cookie"] for cookie in ui.context.cookies(ui.url))
        ui.page.evaluate(
            "(value) => window.localStorage.setItem('private-canary', value)",
            values["storage"],
        )
        assert (
            ui.page.evaluate("() => window.localStorage.getItem('private-canary')")
            == values["storage"]
        )
        ui.page.get_by_label("Display Name").fill(values["form"])
        assert ui.page.get_by_label("Display Name").input_value() == values["form"]
        ui.page.evaluate("(value) => console.error(value)", values["console"])
        assert any(values["console"] in value for value in observed_console)
        ui.page.goto(ui.url_for(f"/{values['path']}"))
        assert ui.page.url.endswith(f"/{values['path']}")
        ui.page.evaluate(
            "(target) => document.dispatchEvent(new CustomEvent('htmx:afterSwap', "
            + "{detail: {target: `#${target}`}}))",
            values["target"],
        )
        assert any(event.target == values["target"] for event in ui.events)
        raise RuntimeError(values["exception"])
