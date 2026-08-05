"""HDJ async filter/global I/O budgets, deadlines, and cancellation (phase 0.13)."""

from __future__ import annotations

import asyncio
import inspect
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, TypeVar

from hedron_core.diagnostics import error

__all__ = [
    "AsyncIoBudget",
    "AsyncIoDeclaration",
    "AsyncIoRegistry",
    "run_declared_async_io",
]

T = TypeVar("T")


@dataclass(slots=True)
class AsyncIoBudget:
    """Per-operation budget for HDJ async I/O."""

    max_operations: int = 32
    deadline_seconds: float | None = 5.0


@dataclass(slots=True)
class AsyncIoDeclaration:
    """Declared async filter or global callable."""

    name: str
    kind: str  # "filter" | "global"
    fn: Callable[..., Any]
    budget: AsyncIoBudget = field(default_factory=AsyncIoBudget)


class AsyncIoRegistry:
    def __init__(self) -> None:
        self._items: dict[str, AsyncIoDeclaration] = {}

    def declare(
        self,
        name: str,
        fn: Callable[..., Any],
        *,
        kind: str = "filter",
        budget: AsyncIoBudget | None = None,
    ) -> AsyncIoDeclaration:
        decl = AsyncIoDeclaration(name=name, kind=kind, fn=fn, budget=budget or AsyncIoBudget())
        self._items[name] = decl
        return decl

    def get(self, name: str) -> AsyncIoDeclaration | None:
        return self._items.get(name)

    def items(self) -> Mapping[str, AsyncIoDeclaration]:
        return dict(self._items)


async def run_declared_async_io(
    decl: AsyncIoDeclaration,
    *args: Any,
    cancel_event: asyncio.Event | None = None,
    trace_correlation_id: str | None = None,
    **kwargs: Any,
) -> Any:
    """Execute a declared async I/O operation with deadline and cancellation.

    Final HDJ render remains synchronous after all declared I/O completes.
    """
    del trace_correlation_id  # correlation is carried by callers into tracing spans
    budget = decl.budget
    deadline = (
        time.monotonic() + budget.deadline_seconds if budget.deadline_seconds is not None else None
    )

    async def _call() -> Any:
        if cancel_event is not None and cancel_event.is_set():
            raise error(
                "HED-PREPARE-0001",
                title="HDJ async I/O cancelled",
                explanation=f"Declared async {decl.kind} {decl.name!r} was cancelled.",
            )
        if deadline is not None and time.monotonic() >= deadline:
            raise error(
                "HED-PREPARE-0002",
                title="HDJ async I/O deadline exceeded",
                explanation=f"Declared async {decl.kind} {decl.name!r} exceeded its deadline.",
            )
        result = decl.fn(*args, **kwargs)
        if inspect.isawaitable(result):
            return await result
        return result

    if budget.deadline_seconds is None:
        return await _call()
    try:
        return await asyncio.wait_for(_call(), timeout=budget.deadline_seconds)
    except TimeoutError as exc:
        raise error(
            "HED-PREPARE-0002",
            title="HDJ async I/O deadline exceeded",
            explanation=f"Declared async {decl.kind} {decl.name!r} exceeded its deadline.",
        ) from exc


async def await_if_needed(value: T | Awaitable[T]) -> T:
    if inspect.isawaitable(value):
        return await value  # type: ignore[no-any-return]
    return value  # type: ignore[return-value]
