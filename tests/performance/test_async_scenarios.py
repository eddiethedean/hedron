"""Scenario overload/degradation without wall-clock sleeps (PERF-013-SCENARIO)."""

from __future__ import annotations

import asyncio

import pytest

from hedron.concurrency import (
    ConcurrencyLimiter,
    configure_concurrency,
    reset_concurrency_for_tests,
)
from hedron_core.diagnostics import HedronError
from hedron_core.testing import AsyncScenario, ControllableClock, assert_ordered_events


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_concurrency_for_tests()
    yield
    reset_concurrency_for_tests()


@pytest.mark.anyio
async def test_overload_degrade_shutdown_scenario() -> None:
    scenario = AsyncScenario(clock=ControllableClock())
    limiter = ConcurrencyLimiter(configure_concurrency(enabled=True, max_in_flight=1, degrade_at=1))
    release = asyncio.Event()

    async def hold() -> str:
        scenario.record("hold:start")
        await release.wait()
        scenario.record("hold:end")
        return "done"

    async def noop() -> None:
        return None

    async def body() -> None:
        task = asyncio.create_task(limiter.run(hold()))
        await asyncio.sleep(0)
        scenario.record("overload:attempt")
        with pytest.raises(HedronError):
            await limiter.run(noop())
        scenario.record("overload:rejected")
        release.set()
        assert await task == "done"
        scenario.record("shutdown:drained")

    await scenario.run(body)
    assert_ordered_events(
        scenario.events,
        [
            "scenario:start",
            "hold:start",
            "overload:attempt",
            "overload:rejected",
            "hold:end",
            "shutdown:drained",
            "scenario:success",
        ],
    )
    assert limiter.overload_count >= 1
