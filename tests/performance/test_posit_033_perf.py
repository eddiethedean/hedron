"""PERF-033: in-process p95 ceilings for inactive / Workbench / native Connect."""

from __future__ import annotations

import statistics
import time

import pytest
from starlette.requests import Request

from hedron_posit import (
    ConnectConfig,
    HedronPosit,
    PositConfig,
    PositProduct,
    resolve_posit_deployment,
    resolve_product,
)
from hedron_posit.config import WorkbenchConfig, WorkbenchMode
from hedron_posit.connect import native_connect_base_from_request

pytestmark = pytest.mark.performance

_P95_MS = 5.0
_N = 1000


def _p95_ms(samples: list[float]) -> float:
    ordered = sorted(samples)
    # nearest-rank p95
    idx = min(len(ordered) - 1, max(0, int(0.95 * len(ordered)) - 1))
    return ordered[idx] * 1000.0


def test_inactive_product_resolution_p95() -> None:
    samples: list[float] = []
    env: dict[str, str] = {}
    for _ in range(_N):
        t0 = time.perf_counter()
        resolve_product(environ=env)
        samples.append(time.perf_counter() - t0)
    assert _p95_ms(samples) <= _P95_MS


def test_workbench_resolve_p95() -> None:
    samples: list[float] = []
    env = {
        "RS_SERVER_URL": "https://wb.example/",
        "HEDRON_WORKBENCH_RESOLVED_MOUNT": "/s/session/p/1",
        "HEDRON_WORKBENCH_RESOLVED_PUBLIC_BASE": "https://wb.example/s/session/p/1",
        "HEDRON_WORKBENCH_RESOLVED_MODE": "on",
        "HEDRON_WORKBENCH_RESOLVED_SOURCE": "test",
    }
    cfg = PositConfig(
        product=PositProduct.WORKBENCH,
        workbench=WorkbenchConfig(mode=WorkbenchMode.ON, mount="/s/session/p/1"),
    )
    for _ in range(_N):
        t0 = time.perf_counter()
        resolve_posit_deployment(cfg, environ=env)
        samples.append(time.perf_counter() - t0)
    assert _p95_ms(samples) <= _P95_MS


def test_native_connect_base_validation_p95(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POSIT_PRODUCT", "CONNECT")
    mount = "/content/00000000-0000-4000-8000-000000000001"
    base = f"https://connect.example{mount}"
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "https",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "root_path": mount,
        "headers": [(b"rstudio-connect-app-base-url", base.encode())],
        "client": ("127.0.0.1", 12345),
        "server": ("connect.example", 443),
    }
    request = Request(scope)
    samples: list[float] = []
    env = {"POSIT_PRODUCT": "CONNECT"}
    for _ in range(_N):
        t0 = time.perf_counter()
        native_connect_base_from_request(
            request,
            product=PositProduct.CONNECT,
            environ=env,
        )
        samples.append(time.perf_counter() - t0)
    p95 = _p95_ms(samples)
    # Keep a cheap sanity on median so a totally broken path fails loudly.
    assert statistics.median(samples) * 1000.0 <= _P95_MS
    assert p95 <= _P95_MS


def test_inactive_facade_construction_budget() -> None:
    # Construction is heavier than pure resolve; still stay well under a soft ceiling.
    samples: list[float] = []
    for _ in range(50):
        t0 = time.perf_counter()
        HedronPosit(
            session_secret="perf-secret-not-for-production",
            posit=PositConfig(connect=ConnectConfig()),
        )
        samples.append(time.perf_counter() - t0)
    assert _p95_ms(samples) <= 50.0
