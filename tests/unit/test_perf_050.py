"""PERF-050 small/medium/large fixture query budgets."""

from __future__ import annotations

import time

from starlette.requests import Request
from tests.unit._helpers_050 import reset_050

from hedron_core.registry import register_component, reset_registry_for_tests
from hedron_explorer.services.catalog import page_components


def setup_function() -> None:
    reset_050()
    reset_registry_for_tests()


def _fill(n: int) -> None:
    for i in range(n):
        register_component(
            logical_id=f"perf.comp{i:04d}",
            name=f"P{i:04d}",
            module="perf",
            distribution="perf",
        )


def _http_request() -> Request:
    return Request(
        {
            "type": "http",
            "asgi": {"spec_version": "2.3", "version": "3.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "headers": [],
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
        }
    )


def test_small_medium_large_query_budget() -> None:
    for size in (10, 200, 2000):
        reset_registry_for_tests()
        _fill(size)
        started = time.perf_counter()
        page = page_components(_http_request())
        elapsed = time.perf_counter() - started
        assert len(page.items) <= 200
        assert elapsed < 2.0
