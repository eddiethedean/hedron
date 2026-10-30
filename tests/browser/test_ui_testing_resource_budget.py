"""Collect timing and bounded-event samples for the frozen browser budget."""

from __future__ import annotations

import importlib.metadata
import json
import os
import time
from typing import Protocol

import pytest
from playwright.sync_api import Browser

from hedron.testing.browser_scenario import BrowserScenarioFactory

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(
        os.environ.get("HEDRON_BROWSER") != "1",
        reason="Opt-in Linux browser evidence: set HEDRON_BROWSER=1",
    ),
]


class _RecordProperty(Protocol):
    def __call__(self, name: str, value: object) -> None: ...


def test_ui_testing_resource_budget(
    browser: Browser,
    hedron_ui: BrowserScenarioFactory,
    record_property: _RecordProperty,
) -> None:
    context_create_ms: list[float] = []
    context_close_ms: list[float] = []
    for _ in range(10):
        started = time.perf_counter()
        context = browser.new_context(service_workers="block")
        context_create_ms.append((time.perf_counter() - started) * 1000)
        stopped = time.perf_counter()
        context.close()
        context_close_ms.append((time.perf_counter() - stopped) * 1000)

    scenario_started = time.perf_counter()
    with hedron_ui.from_app(
        "hedron.testing.examples.profile_app:create_app",
        config={"title": "Browser resource budget"},
    ) as ui:
        ui.page.goto(ui.url)
        name = ui.page.get_by_label("Display Name")
        name.fill("Ada Lovelace")
        checkpoint = ui.checkpoint()
        name.press("Enter")
        settled = ui.settle(since=checkpoint, target="hedron-errors")
        assert settled.status == 200
        event_snapshot = [
            {
                "sequence": event.sequence,
                "navigation_epoch": event.navigation_epoch,
                "kind": event.kind,
                "request_id": event.request_id,
                "status": event.status,
                "generation": event.generation,
            }
            for event in ui.events
        ]
        record_property("settle_ms", json.dumps([settled.elapsed_seconds * 1000]))
        record_property("event_count", str(len(event_snapshot)))
        record_property(
            "event_snapshot_bytes",
            str(len(json.dumps(event_snapshot, separators=(",", ":"), sort_keys=True).encode())),
        )
    scenario_cycle_ms = (time.perf_counter() - scenario_started) * 1000

    record_property("context_create_ms", json.dumps(context_create_ms))
    record_property("context_close_ms", json.dumps(context_close_ms))
    record_property("scenario_cycle_ms", str(scenario_cycle_ms))
    record_property("playwright_version", importlib.metadata.version("playwright"))
    record_property("pytest_playwright_version", importlib.metadata.version("pytest-playwright"))
    record_property("browser_version", browser.version)
    assert max(context_create_ms) < 5_000
    assert max(context_close_ms) < 5_000
    assert scenario_cycle_ms < 15_000
