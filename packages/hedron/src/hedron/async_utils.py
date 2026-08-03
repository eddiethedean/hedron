"""Async helpers including gather/run_sync contracts (phase 0.7B)."""

from __future__ import annotations

import asyncio
import contextvars
import functools
import inspect
from collections.abc import Awaitable, Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any, TypeVar

T = TypeVar("T")

__all__ = [
    "await_if_needed",
    "gather",
    "is_async_callable",
    "run_sync",
    "set_run_sync_executor",
]

_CPU_HEAVY = object()
_executor: ThreadPoolExecutor | None = None
_executor_workers = 4


def is_async_callable(fn: Callable[..., Any]) -> bool:
    return inspect.iscoroutinefunction(fn) or inspect.isasyncgenfunction(fn)


async def await_if_needed(value: T | Awaitable[T]) -> T:
    if inspect.isawaitable(value):
        return await value  # type: ignore[no-any-return]
    return value  # type: ignore[return-value]


def mark_cpu_heavy(fn: Callable[..., T]) -> Callable[..., T]:
    """Mark a callable as unsuitable for run_sync thread offload."""
    fn.__hedron_cpu_heavy__ = True
    return fn


def set_run_sync_executor(*, max_workers: int = 4) -> None:
    global _executor, _executor_workers
    if _executor is not None:
        _executor.shutdown(wait=False)
    _executor_workers = max_workers
    _executor = ThreadPoolExecutor(max_workers=max_workers)


def _get_executor() -> ThreadPoolExecutor:
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=_executor_workers)
    return _executor


async def gather(
    *aws: Awaitable[Any],
    return_exceptions: bool = False,
) -> list[Any]:
    """Gather sibling awaitables with ContextVar propagation via task creation.

    When ``return_exceptions`` is False, the first exception cancels remaining
    siblings (asyncio.gather default behavior).
    """
    if not aws:
        return []
    return list(await asyncio.gather(*aws, return_exceptions=return_exceptions))


async def run_sync(fn: Callable[..., T], /, *args: Any, **kwargs: Any) -> T:
    """Run a sync callable in a bounded thread pool with ContextVar copy.

    Callables marked with ``mark_cpu_heavy`` are rejected — apps should use a
    durable job backend for CPU-heavy work (D-020 / D-037).
    """
    if getattr(fn, "__hedron_cpu_heavy__", False):
        raise ValueError("CPU-heavy callables are rejected by run_sync; use JobBackend")
    loop = asyncio.get_running_loop()
    ctx = contextvars.copy_context()
    bound = functools.partial(ctx.run, fn, *args, **kwargs)
    return await loop.run_in_executor(_get_executor(), bound)
