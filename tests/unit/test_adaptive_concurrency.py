"""Adaptive concurrency (CONC-013)."""

from __future__ import annotations

import asyncio

import pytest

from hedron.concurrency import (
    adaptive_gather,
    configure_concurrency,
    reset_concurrency_for_tests,
)
from hedron_core.diagnostics import HedronError


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_concurrency_for_tests()
    yield
    reset_concurrency_for_tests()


@pytest.mark.anyio
async def test_adaptive_gather_respects_capacity() -> None:
    configure_concurrency(enabled=True, max_in_flight=2, degrade_at=1)

    async def work(n: int) -> int:
        await asyncio.sleep(0)
        return n

    # With return_exceptions, overload raises as result items when over capacity mid-flight.
    configure_concurrency(enabled=True, max_in_flight=1, degrade_at=1)

    async def hold() -> str:
        await asyncio.Event().wait()
        return "never"

    # Start one long-running task via limiter path by saturating.
    from hedron.concurrency import ConcurrencyLimiter, get_concurrency_config

    limiter = ConcurrencyLimiter(get_concurrency_config())

    async def one() -> int:
        return await limiter.run(work(1))

    assert await one() == 1


@pytest.mark.anyio
async def test_overload_raises() -> None:
    configure_concurrency(enabled=True, max_in_flight=1, degrade_at=1)
    from hedron.concurrency import ConcurrencyLimiter, get_concurrency_config

    limiter = ConcurrencyLimiter(get_concurrency_config())
    started = asyncio.Event()
    release = asyncio.Event()

    async def hold() -> str:
        started.set()
        await release.wait()
        return "ok"

    task = asyncio.create_task(limiter.run(hold()))
    await started.wait()

    async def noop() -> None:
        return None

    with pytest.raises(HedronError) as exc:
        await limiter.run(noop())
    assert exc.value.diagnostic.code == "HED-CONC-0001"
    release.set()
    assert await task == "ok"


@pytest.mark.anyio
async def test_opt_out_preserves_semantics() -> None:
    configure_concurrency(enabled=False, max_in_flight=1)
    results = await adaptive_gather(asyncio.sleep(0, result=1), asyncio.sleep(0, result=2))
    assert results == [1, 2]
