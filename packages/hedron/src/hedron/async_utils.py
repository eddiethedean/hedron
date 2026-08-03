"""Async helpers for sync/async endpoint parity."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

T = TypeVar("T")

__all__ = ["await_if_needed", "is_async_callable"]


def is_async_callable(fn: Callable[..., Any]) -> bool:
    return inspect.iscoroutinefunction(fn) or inspect.isasyncgenfunction(fn)


async def await_if_needed(value: T | Awaitable[T]) -> T:
    if inspect.isawaitable(value):
        return await value  # type: ignore[no-any-return]
    return value  # type: ignore[return-value]
