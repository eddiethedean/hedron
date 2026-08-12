"""Async cache single-flight cancellation isolation (#158)."""

from __future__ import annotations

import asyncio

import pytest

from hedron_core.cache import InMemoryCacheBackend


@pytest.mark.anyio
async def test_single_flight_async_owner_cancel_does_not_poison_waiter() -> None:
    backend = InMemoryCacheBackend()
    started = asyncio.Event()
    release = asyncio.Event()
    loads = 0

    async def loader() -> str:
        nonlocal loads
        loads += 1
        started.set()
        await release.wait()
        return "ok"

    async def owner() -> str:
        return await backend.single_flight_async("k", loader)

    async def waiter() -> str:
        await started.wait()
        return await backend.single_flight_async("k", loader)

    owner_task = asyncio.create_task(owner())
    await started.wait()
    waiter_task = asyncio.create_task(waiter())
    await asyncio.sleep(0.05)
    owner_task.cancel()
    release.set()

    owner_result, waiter_result = await asyncio.gather(
        owner_task, waiter_task, return_exceptions=True
    )
    assert isinstance(owner_result, asyncio.CancelledError)
    assert waiter_result == "ok"
    assert loads == 2  # owner started one load; waiter became owner and finished


@pytest.mark.anyio
async def test_single_flight_async_still_shares_successful_load() -> None:
    backend = InMemoryCacheBackend()
    started = asyncio.Event()
    release = asyncio.Event()
    loads = 0

    async def loader() -> str:
        nonlocal loads
        loads += 1
        started.set()
        await release.wait()
        return "shared"

    async def call() -> str:
        return await backend.single_flight_async("shared-key", loader)

    first = asyncio.create_task(call())
    await started.wait()
    second = asyncio.create_task(call())
    await asyncio.sleep(0.05)
    release.set()
    assert await asyncio.gather(first, second) == ["shared", "shared"]
    assert loads == 1
