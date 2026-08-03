"""Tests for gather/run_sync."""

from __future__ import annotations

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
