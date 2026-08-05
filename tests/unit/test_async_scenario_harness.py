"""Async scenario harness (ASYNC-TEST-013)."""

from __future__ import annotations

import asyncio

import pytest

from hedron_core.testing import (
    AsyncScenario,
    ControllableClock,
    assert_ordered_events,
    scripted_outcome,
)


def test_controllable_clock_advances_without_sleep() -> None:
    clock = ControllableClock()
    assert clock.monotonic() == 0.0
    clock.advance(2.5)
    assert clock.monotonic() == 2.5


@pytest.mark.anyio
async def test_scripted_success_and_fail() -> None:
    ok = scripted_outcome("dep", outcome="success", value=42)
    assert await ok.run() == 42
    bad = scripted_outcome("dep", outcome="fail")
    with pytest.raises(RuntimeError):
        await bad.run()


@pytest.mark.anyio
async def test_hang_until_cancel_and_ordered_events() -> None:
    scenario = AsyncScenario()
    dep = scripted_outcome("slow", outcome="hang_until_cancel")

    async def _run() -> None:
        task = asyncio.create_task(dep.run(cancel_event=scenario.cancel_event))
        scenario.record("scheduled")
        scenario.trigger_cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    await scenario.run(_run)
    assert_ordered_events(
        scenario.events + dep.events,
        ["scenario:start", "scheduled", "cancel", "slow:start", "slow:cancelled"],
    )
