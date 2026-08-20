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
    started = asyncio.Event()
    release = asyncio.Event()
    results: list[int] = []

    async def hold(n: int) -> int:
        started.set()
        await release.wait()
        results.append(n)
        return n

    task = asyncio.create_task(adaptive_gather(hold(1), return_exceptions=True))
    await started.wait()

    # degrade_at=1 with one in-flight → further work is shed.
    second = await adaptive_gather(asyncio.sleep(0, result=2), return_exceptions=True)
    assert len(second) == 1
    assert isinstance(second[0], HedronError)
    assert second[0].diagnostic.code == "HED-CONC-0001"

    release.set()
    first = await task
    assert first == [1]


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
async def test_degrade_at_sheds_before_max() -> None:
    configure_concurrency(enabled=True, max_in_flight=8, degrade_at=1)
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
    with pytest.raises(HedronError) as exc:
        await limiter.run(asyncio.sleep(0))
    assert exc.value.diagnostic.code == "HED-CONC-0001"
    assert limiter.overload_count >= 1
    release.set()
    assert await task == "ok"


@pytest.mark.anyio
async def test_opt_out_preserves_semantics() -> None:
    configure_concurrency(enabled=False, max_in_flight=1)
    results = await adaptive_gather(asyncio.sleep(0, result=1), asyncio.sleep(0, result=2))
    assert results == [1, 2]


@pytest.mark.anyio
async def test_issue_103_cancels_siblings_on_overload() -> None:
    configure_concurrency(enabled=True, max_in_flight=2, degrade_at=1)
    started = asyncio.Event()
    release = asyncio.Event()
    cancelled: list[int] = []

    async def hold(n: int) -> int:
        started.set()
        try:
            await release.wait()
        except asyncio.CancelledError:
            cancelled.append(n)
            raise
        return n

    gather_task = asyncio.create_task(
        adaptive_gather(hold(1), hold(2), return_exceptions=True)
    )
    await started.wait()
    results = await gather_task

    overloads = [
        r
        for r in results
        if isinstance(r, HedronError) and r.diagnostic.code == "HED-CONC-0001"
    ]
    assert len(overloads) >= 1
    assert 1 in cancelled
    release.set()
