"""Tests for gather/run_sync."""

from __future__ import annotations

import asyncio
from contextvars import ContextVar

import pytest

from hedron.async_utils import gather, mark_cpu_heavy, run_sync

cv: ContextVar[str] = ContextVar("cv", default="")

pytestmark = pytest.mark.anyio


async def test_gather_basic() -> None:
    async def one() -> int:
        return 1

    async def two() -> int:
        return 2

    assert await gather(one(), two()) == [1, 2]


async def test_gather_cancels_and_drains_siblings_after_failure() -> None:
    started = asyncio.Event()
    cancelled = asyncio.Event()

    async def slow() -> None:
        started.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            cancelled.set()
            raise

    async def fail() -> None:
        await started.wait()
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        await gather(slow(), fail())
    assert cancelled.is_set()


async def test_run_sync_propagates_contextvar() -> None:
    cv.set("hello")

    def read() -> str:
        return cv.get()

    assert await run_sync(read) == "hello"


async def test_run_sync_rejects_cpu_heavy() -> None:
    @mark_cpu_heavy
    def heavy() -> int:
        return 1

    with pytest.raises(ValueError, match="CPU-heavy"):
        await run_sync(heavy)
