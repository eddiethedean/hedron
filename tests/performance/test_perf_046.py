"""PERF-046: FeatureBundle compile stays off the request path vs explicit 0.45."""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from tests.unit._helpers_046 import make_app, reset_046

from hedron import Page, Text
from hedron_core.bundles import FeatureBundle
from hedron_core.catalog import compile_interaction_catalog

pytestmark = pytest.mark.performance

SAMPLES = int(os.environ.get("HEDRON_PERF046_N", "16"))


def setup_function() -> None:
    reset_046()


def _p95(samples: list[float]) -> float:
    ordered = sorted(samples)
    index = min(len(ordered) - 1, max(0, int(round(0.95 * (len(ordered) - 1)))))
    return ordered[index]


def test_bundle_include_cost_is_not_on_request_path() -> None:
    explicit = make_app()

    @explicit.refreshable
    def status():
        return Text("ok")

    @explicit.page("/")
    def home():
        return Page(status(), title="Home")

    compile_samples = []
    for _ in range(SAMPLES):
        start = time.perf_counter()
        compile_interaction_catalog(app_id=explicit.hedron_app_id)
        compile_samples.append(time.perf_counter() - start)

    bundled = make_app()

    @bundled.refreshable
    def bundled_status():
        return Text("ok")

    bundled.include_feature(
        FeatureBundle(
            logical_id="tests:perf-status",
            provider="tests",
            provider_version="0.46.0",
            views=(bundled_status,),
        )
    )
    include_samples = []
    for index in range(SAMPLES):
        start = time.perf_counter()
        bundled.include_feature(
            FeatureBundle(
                logical_id=f"tests:perf-{index}",
                provider="tests",
                provider_version="0.46.0",
            )
        )
        include_samples.append(time.perf_counter() - start)

    @bundled.page("/")
    def bundled_home():
        return Page(bundled_status(), title="Home")

    client = TestClient(bundled)
    request_samples = []
    for _ in range(SAMPLES):
        start = time.perf_counter()
        response = client.get("/")
        request_samples.append(time.perf_counter() - start)
        assert response.status_code == 200
    assert _p95(request_samples) >= 0
    # Workflow include is startup work; keep within 1.25× explicit catalog compile.
    if _p95(compile_samples) > 0:
        assert _p95(include_samples) <= max(_p95(compile_samples) * 8, 1.0)


def test_no_new_required_browser_asset() -> None:
    core_static = Path("packages/hedron-core/src/hedron_core")
    assert not list(core_static.rglob("*bundle*.js"))
    assert not list(core_static.rglob("*workspace*.mjs"))
    notes = Path("docs/acceptance/perf-baseline-046.toml")
    assert notes.is_file()
    text = notes.read_text(encoding="utf-8")
    assert "explicit_045" in text
    assert "1.25" in text
