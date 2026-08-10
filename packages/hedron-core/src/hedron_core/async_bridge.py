"""Run async coroutines from sync adapter paths (Flask / sync Django)."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, TypeVar

__all__ = ["run_coro", "run_prepare", "running_loop"]

T = TypeVar("T")


def running_loop() -> bool:
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


def run_coro(awaitable: Awaitable[T] | Coroutine[Any, Any, T]) -> T:
    """Run a coroutine when no event loop is running; refuse nested loops.

    Flask and sync Django call this before ``render``. When already inside an
    async loop (ASGI Django), callers should ``await`` the coroutine from the
    ASGI path instead — do not create the coroutine before checking
    :func:`running_loop`.
    """
    if running_loop():
        close = getattr(awaitable, "close", None)
        if callable(close):
            close()
        raise RuntimeError(
            "run_coro() cannot be used while an event loop is already running; "
            "await the coroutine from the ASGI path instead."
        )
    return asyncio.run(awaitable)  # type: ignore[arg-type]


def run_prepare(factory: Callable[[], Coroutine[Any, Any, Any]]) -> None:
    """Create and run a prepare coroutine only when no loop is running.

    When a loop is already running, refuse silently-skipping prepare (fail closed)
    so ASGI callers must ``await prepare_tree(...)`` explicitly.
    """
    if running_loop():
        raise RuntimeError(
            "run_prepare() cannot be used while an event loop is already running; "
            "await prepare_tree(...) from the ASGI path instead."
        )
    asyncio.run(factory())
