"""RESILIENCE-050 provider crash isolation and cancellation."""

from __future__ import annotations

from concurrent.futures import TimeoutError as FuturesTimeout

from tests.unit._helpers_050 import reset_050

from hedron_core.plugins import ExplorerProvider
from hedron_explorer.services.provider import run_isolated
from hedron_explorer.services.runtime import reset_explorer_runtime_for_tests


def setup_function() -> None:
    reset_050()


def test_provider_crash_does_not_escape() -> None:
    provider = ExplorerProvider(panel_id="x", title="x", plugin="x")
    result = run_isolated(provider, lambda: 1 / 0)
    assert result["ok"] is False
    assert result["isolated"] is True


def test_timeout_isolation() -> None:
    provider = ExplorerProvider(panel_id="slow", title="slow", plugin="x", timeout_ms=50)

    def hang() -> str:
        import time

        time.sleep(1)
        return "done"

    result = run_isolated(provider, hang)
    assert result["ok"] is False
    assert result["error"] == "timeout"
    assert FuturesTimeout is not None


def test_runtime_reset_clears_buffers() -> None:
    from hedron_explorer.services.runtime import AUDIT, TRACE

    AUDIT.appendleft({"x": 1})
    TRACE.appendleft({"y": 1})
    reset_explorer_runtime_for_tests()
    assert len(AUDIT) == 0
    assert len(TRACE) == 0
