"""HDJ async filter/global I/O budgets, deadlines, and cancellation (phase 0.13)."""

from __future__ import annotations

import asyncio
import inspect
import time
from collections.abc import Awaitable, Callable, Mapping, MutableMapping
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Protocol, TypeVar, cast

from hedron_core.diagnostics import error

__all__ = [
    "AsyncIoBudget",
    "AsyncIoDeclaration",
    "AsyncIoRegistry",
    "async_io_session",
    "run_declared_async_io",
]

T = TypeVar("T")

_ops_used: ContextVar[int] = ContextVar("hedron_hdj_async_ops_used", default=0)
_ops_limit: ContextVar[int | None] = ContextVar("hedron_hdj_async_ops_limit", default=None)
_correlation: ContextVar[str | None] = ContextVar("hedron_hdj_async_correlation", default=None)


class _JinjaFilterEnvironment(Protocol):
    """Minimal Jinja environment surface used to bind declared async filters/globals."""

    filters: MutableMapping[str, Callable[..., object]]
    globals: MutableMapping[str, object]


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
    fn: Callable[..., object]
    budget: AsyncIoBudget = field(default_factory=AsyncIoBudget)


class AsyncIoRegistry:
    def __init__(self) -> None:
        self._items: dict[str, AsyncIoDeclaration] = {}

    def declare(
        self,
        name: str,
        fn: Callable[..., object],
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

    def bind_filters(self, environment: _JinjaFilterEnvironment) -> None:
        """Install declared filters/globals that route through ``run_declared_async_io``."""
        for decl in self._items.values():
            if decl.kind == "filter":

                async def _filter(
                    value: object,
                    *args: object,
                    _decl: AsyncIoDeclaration = decl,
                    **kwargs: object,
                ) -> object:
                    return await _run_declared(_decl, (value, *args), kwargs)

                environment.filters[decl.name] = _filter
            else:

                async def _global(
                    *args: object,
                    _decl: AsyncIoDeclaration = decl,
                    **kwargs: object,
                ) -> object:
                    return await _run_declared(_decl, args, kwargs)

                environment.globals[decl.name] = _global


class _AsyncIoSession:
    def __init__(self, *, max_operations: int, correlation_id: str | None) -> None:
        self._max = max_operations
        self._correlation = correlation_id
        self._tok_used: Token[int] | None = None
        self._tok_limit: Token[int | None] | None = None
        self._tok_corr: Token[str | None] | None = None

    def __enter__(self) -> _AsyncIoSession:
        self._tok_used = _ops_used.set(0)
        self._tok_limit = _ops_limit.set(self._max)
        self._tok_corr = _correlation.set(self._correlation)
        return self

    def __exit__(self, *args: object) -> None:
        if self._tok_corr is not None:
            _correlation.reset(self._tok_corr)
        if self._tok_limit is not None:
            _ops_limit.reset(self._tok_limit)
        if self._tok_used is not None:
            _ops_used.reset(self._tok_used)


def async_io_session(
    *,
    max_operations: int = 32,
    correlation_id: str | None = None,
) -> _AsyncIoSession:
    """Bind per-render operation budget and correlation id for declared async I/O."""
    return _AsyncIoSession(max_operations=max_operations, correlation_id=correlation_id)


async def _run_declared(
    decl: AsyncIoDeclaration,
    args: tuple[object, ...],
    kwargs: Mapping[str, object],
    *,
    cancel_event: asyncio.Event | None = None,
    trace_correlation_id: str | None = None,
) -> object:
    """Shared executor for declared async I/O (kwargs kept separate from control params)."""
    correlation = trace_correlation_id or _correlation.get()
    budget = decl.budget
    limit = _ops_limit.get()
    if limit is not None:
        used = _ops_used.get()
        if used >= limit or used >= budget.max_operations:
            raise error(
                "HED-PREPARE-0003",
                title="HDJ async I/O operation budget exceeded",
                explanation=(
                    f"Declared async {decl.kind} {decl.name!r} exceeded max_operations "
                    f"(used={used}, limit={limit}, budget={budget.max_operations})."
                ),
                remediation="Raise AsyncIoBudget.max_operations or reduce declared async calls.",
            )
        _ops_used.set(used + 1)
    elif budget.max_operations <= 0:
        raise error(
            "HED-PREPARE-0003",
            title="HDJ async I/O operation budget exceeded",
            explanation=f"Declared async {decl.kind} {decl.name!r} has max_operations=0.",
        )

    deadline = (
        time.monotonic() + budget.deadline_seconds if budget.deadline_seconds is not None else None
    )

    async def _call() -> object:
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
            return await cast(Awaitable[object], result)
        return result

    # Correlation id is available for tracing exporters / span attributes.
    _ = correlation

    if budget.deadline_seconds is None:
        return await _call()
    try:
        return await asyncio.wait_for(_call(), timeout=budget.deadline_seconds)
    except asyncio.TimeoutError as exc:
        raise error(
            "HED-PREPARE-0002",
            title="HDJ async I/O deadline exceeded",
            explanation=f"Declared async {decl.kind} {decl.name!r} exceeded its deadline.",
        ) from exc


async def run_declared_async_io(
    decl: AsyncIoDeclaration,
    *args: object,
    cancel_event: asyncio.Event | None = None,
    trace_correlation_id: str | None = None,
    **kwargs: object,
) -> object:
    """Execute a declared async I/O operation with deadline and cancellation.

    Final HDJ render remains synchronous after all declared I/O completes.
    """
    return await _run_declared(
        decl,
        args,
        kwargs,
        cancel_event=cancel_event,
        trace_correlation_id=trace_correlation_id,
    )


async def await_if_needed(value: T | Awaitable[T]) -> T:
    if inspect.isawaitable(value):
        return await cast(Awaitable[T], value)
    return cast(T, value)
