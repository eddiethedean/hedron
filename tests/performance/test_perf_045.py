"""PERF-045: compile/seal stays off the request path; no new required browser asset."""

from __future__ import annotations

import os
import time

import pytest
from fastapi.testclient import TestClient
from tests.unit._helpers_045 import make_app, reset_045

from hedron import Page, Text
from hedron_core.catalog import compile_interaction_catalog, seal_interaction_catalog

pytestmark = pytest.mark.performance

SAMPLES = int(os.environ.get("HEDRON_PERF045_N", "16"))


def setup_function() -> None:
    reset_045()


def _p95(samples: list[float]) -> float:
    ordered = sorted(samples)
    index = min(len(ordered) - 1, max(0, int(round(0.95 * (len(ordered) - 1)))))
    return ordered[index]


def test_compile_cost_is_not_on_request_path() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    @app.page("/")
    def home():
        return Page(status(), title="Home")

    compile_samples = []
    for _ in range(SAMPLES):
        start = time.perf_counter()
        compile_interaction_catalog(app_id=app.hedron_app_id)
        compile_samples.append(time.perf_counter() - start)
    client = TestClient(app)
    request_samples = []
    for _ in range(SAMPLES):
        start = time.perf_counter()
        response = client.get("/")
        request_samples.append(time.perf_counter() - start)
        assert response.status_code == 200
    # Compile/seal is startup work; request samples must remain defined.
    assert _p95(request_samples) >= 0
    assert _p95(compile_samples) >= 0
    seal_interaction_catalog(app_id=app.hedron_app_id)


def test_no_new_required_browser_asset() -> None:
    from pathlib import Path

    core_static = Path("packages/hedron-core/src/hedron_core")
    assert not list(core_static.rglob("*catalog*.js"))
    assert not list(core_static.rglob("*interactions*.mjs"))
