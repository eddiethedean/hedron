"""PERF-043: handle path stays within 10% and 1ms of the region baseline."""

from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient
from tests.unit._helpers_043 import make_app, reset_043

from hedron import Hedron, Page, Text, swap
from hedron_core.registry import reset_registry_for_tests

pytestmark = pytest.mark.performance


def setup_function() -> None:
    reset_043()


def _p95(samples: list[float]) -> float:
    ordered = sorted(samples)
    index = min(len(ordered) - 1, max(0, int(round(0.95 * (len(ordered) - 1)))))
    return ordered[index]


def _timed_gets(client: TestClient, path: str, headers: dict[str, str], n: int = 40) -> list[float]:
    samples: list[float] = []
    for _ in range(n):
        start = time.perf_counter()
        response = client.get(path, headers=headers)
        elapsed = time.perf_counter() - start
        assert response.status_code == 200
        samples.append(elapsed)
    return samples


def test_handle_p95_within_region_baseline() -> None:
    region_app = Hedron(
        title="region",
        security="development",
        explorer="off",
        session_secret="secret-for-tests-32chars-ok!!",
    )
    region = region_app.region("panel", description="baseline")

    @region_app.page("/", fragment_regions=(region,))
    def home():
        return Page(Text("home"), title="Home")

    @region_app.fragment("/panel", region=region)
    def panel():
        return swap(Text("panel"))

    handle_app = make_app()

    @handle_app.refreshable
    def status():
        return Text("panel")

    @handle_app.page("/")
    def handle_home():
        return Page(status(), title="Home")

    region_client = TestClient(region_app)
    handle_client = TestClient(handle_app)
    region_headers = {"HX-Request": "true", "HX-Target": "panel"}
    handle_headers = {"HX-Request": "true", "HX-Target": status.dom_id}
    region_samples = _timed_gets(region_client, "/panel", region_headers)
    handle_samples = _timed_gets(handle_client, status.path, handle_headers)
    region_p95 = _p95(region_samples)
    handle_p95 = _p95(handle_samples)
    assert handle_p95 <= region_p95 * 1.10 + 0.001


def test_no_required_extra_asset_and_fan_out_payloads() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    @app.page("/")
    def home():
        return Page(status(), title="Home")

    client = TestClient(app)
    page = client.get("/")
    assert page.status_code == 200
    assert "htmx.min.js" in page.text
    assert "hedron-handle.js" not in page.text.lower()
    from hedron import refresh
    from hedron_core.updates import compile_to_interaction

    compiled = compile_to_interaction(refresh(status), expected_app_id=app.hedron_app_id)
    payload = str(compiled.trigger).encode("utf-8")
    assert len(payload) < 2048


def test_retain_memory_cycles() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("cycle")

    client = TestClient(app)
    headers = {"HX-Request": "true", "HX-Target": status.dom_id}
    for _ in range(24):
        assert client.get(status.path, headers=headers).status_code == 200
    reset_registry_for_tests()
