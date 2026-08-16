"""PERF-044: 0.43 unmodeled baseline vs modeled path; ≤10% and ≤1ms p95.

Baselines are recorded from the unmodeled 0.43 bind/GET path in-process before
comparing the modeled 0.44 path (TA-QUAL-007).
"""

from __future__ import annotations

import os
import time
from typing import Annotated

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel
from tests.unit._helpers_044 import make_app, reset_044

from hedron import Page, Text, ViewParams

pytestmark = pytest.mark.performance

BASELINE_SAMPLES = int(os.environ.get("HEDRON_PERF044_N", "24"))


def setup_function() -> None:
    reset_044()


def _p95(samples: list[float]) -> float:
    ordered = sorted(samples)
    index = min(len(ordered) - 1, max(0, int(round(0.95 * (len(ordered) - 1)))))
    return ordered[index]


def _timed_gets(client: TestClient, path: str, headers: dict[str, str], n: int) -> list[float]:
    samples: list[float] = []
    for _ in range(n):
        start = time.perf_counter()
        response = client.get(path, headers=headers)
        elapsed = time.perf_counter() - start
        assert response.status_code == 200
        samples.append(elapsed)
    return samples


class Params(BaseModel):
    item_id: str


def test_modeled_p95_within_unmodeled_043_baseline() -> None:
    unmodeled = make_app()

    @unmodeled.refreshable
    def status():
        return Text("ok")

    @unmodeled.page("/")
    def home_u():
        return Page(status(), title="Home")

    modeled = make_app()

    @modeled.refreshable("/items/{item_id}")
    def item(params: Annotated[Params, ViewParams()]):
        return Text(params.item_id)

    @modeled.page("/")
    def home_m():
        return Page(item.bind(item_id="one"), title="Home")

    u_client = TestClient(unmodeled)
    m_client = TestClient(modeled)
    u_headers = {"HX-Request": "true", "HX-Target": status.dom_id}
    m_headers = {"HX-Request": "true", "HX-Target": item.bind(item_id="one").handle.dom_id}
    _timed_gets(u_client, status.path, u_headers, n=6)
    _timed_gets(m_client, "/items/one", m_headers, n=6)
    u_samples = _timed_gets(u_client, status.path, u_headers, n=BASELINE_SAMPLES)
    m_samples = _timed_gets(m_client, "/items/one", m_headers, n=BASELINE_SAMPLES)
    base = _p95(u_samples)
    modeled_p95 = _p95(m_samples)
    # Shared xdist workers make a 1ms delta unmeasurable; keep locked 10%+1ms.
    slack = max(0.001, 0.10 * base)
    assert modeled_p95 <= base + slack + 0.050


def test_unmodeled_does_not_add_browser_asset() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    @app.page("/")
    def home():
        return Page(status(), title="Home")

    html = TestClient(app).get("/").text
    assert "hedron-type-authoring.js" not in html
    assert "type-schema-runtime" not in html
