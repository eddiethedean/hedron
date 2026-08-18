"""PERF-050 small/medium/large fixture query budgets."""

from __future__ import annotations

import time

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


def test_small_medium_large_query_budget() -> None:
    for size in (10, 200, 2000):
        reset_registry_for_tests()
        _fill(size)
        started = time.perf_counter()
        page = page_components()
        elapsed = time.perf_counter() - started
        assert len(page.items) <= 200
        assert elapsed < 2.0
