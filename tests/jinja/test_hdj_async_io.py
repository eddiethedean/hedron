"""HDJ async I/O budgets (HDJ-DEF-013)."""

from __future__ import annotations

import asyncio
import math

import pytest

from hedron_core.diagnostics import HedronError
from hedron_jinja import AsyncIoBudget, AsyncIoRegistry, run_declared_async_io


@pytest.mark.anyio
async def test_declared_async_filter_runs() -> None:
    registry = AsyncIoRegistry()

    async def load_user(uid: str) -> str:
        await asyncio.sleep(0)
        return f"user:{uid}"

    decl = registry.declare("load_user", load_user, kind="filter")
    assert await run_declared_async_io(decl, "42") == "user:42"


@pytest.mark.anyio
async def test_deadline_exceeded() -> None:
    registry = AsyncIoRegistry()

    async def slow() -> str:
        await asyncio.sleep(0.05)
        return "x"

    decl = registry.declare(
        "slow",
        slow,
        kind="global",
        budget=AsyncIoBudget(deadline_seconds=0.001),
    )
    with pytest.raises(HedronError) as exc:
        await run_declared_async_io(decl)
    assert exc.value.diagnostic.code == "HED-PREPARE-0002"


@pytest.mark.anyio
async def test_cancellation() -> None:
    registry = AsyncIoRegistry()
    cancel = asyncio.Event()
    cancel.set()

    async def work() -> str:
        return "x"

    decl = registry.declare("work", work)
    with pytest.raises(HedronError) as exc:
        await run_declared_async_io(decl, cancel_event=cancel)
    assert exc.value.diagnostic.code == "HED-PREPARE-0001"


@pytest.mark.parametrize("deadline", [math.nan, math.inf, 0.0, -1.0])
def test_async_io_budget_rejects_invalid_deadlines(deadline: float) -> None:
    with pytest.raises(ValueError, match="deadline_seconds"):
        AsyncIoBudget(deadline_seconds=deadline)
