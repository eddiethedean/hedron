"""Async cache single-flight cancellation isolation (#158) and cross-loop safety (#99)."""

from __future__ import annotations

import asyncio
import threading

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


def test_single_flight_async_safe_across_event_loops() -> None:
    """#99: waiters on a different loop must not await the owner's Future."""
    backend = InMemoryCacheBackend()
    owner_started = threading.Event()
    release_owner = threading.Event()
    results: dict[str, object] = {}
    errors: dict[str, BaseException] = {}

    async def owner_loader() -> str:
        owner_started.set()
        while not release_owner.is_set():
            await asyncio.sleep(0.01)
        return "owner-value"

    def run_owner() -> None:
        async def _run() -> None:
            try:
                results["owner"] = await backend.single_flight_async("cross-loop", owner_loader)
            except BaseException as exc:  # noqa: BLE001 - capture for assertion
                errors["owner"] = exc

        asyncio.run(_run())

    def run_waiter() -> None:
        owner_started.wait(timeout=2.0)

        async def _run() -> None:
            try:
                # Independent load on this loop — must not crash with cross-loop Future.
                results["waiter"] = await backend.single_flight_async(
                    "cross-loop", lambda: "waiter-value"
                )
            except BaseException as exc:  # noqa: BLE001
                errors["waiter"] = exc

        asyncio.run(_run())

    owner_thread = threading.Thread(target=run_owner)
    waiter_thread = threading.Thread(target=run_waiter)
    owner_thread.start()
    assert owner_started.wait(timeout=2.0)
    waiter_thread.start()
    waiter_thread.join(timeout=5.0)
    release_owner.set()
    owner_thread.join(timeout=5.0)

    assert errors == {}, f"unexpected errors: {errors}"
    assert results["owner"] == "owner-value"
    assert results["waiter"] in {"owner-value", "waiter-value"}
    assert not backend._async_flights
