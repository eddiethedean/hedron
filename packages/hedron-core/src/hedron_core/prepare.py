"""Optional component prepare() lifecycle (phase 0.13)."""

from __future__ import annotations

import asyncio
import inspect
import time
from collections.abc import Awaitable, Callable, Mapping, Sequence
from contextvars import ContextVar
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, TypeVar

from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error

__all__ = [
    "PartialFailurePolicy",
    "PrepareContext",
    "PrepareTiming",
    "collect_prepare_targets",
    "prepare_tree",
    "reset_prepare_for_tests",
]

T = TypeVar("T")

_active_prepare: ContextVar[PrepareContext | None] = ContextVar(
    "hedron_prepare_context", default=None
)


class PartialFailurePolicy(StrEnum):
    """How sibling prepare failures interact."""

    FAIL_FAST = "fail_fast"
    CONTINUE = "continue"


@dataclass(slots=True)
class PrepareTiming:
    """Explorer-facing prepare timing record."""

    logical_id: str
    started_at: float
    finished_at: float
    cancelled: bool = False
    error: str | None = None

    @property
    def duration_ms(self) -> float:
        return max(0.0, (self.finished_at - self.started_at) * 1000.0)


@dataclass
class PrepareContext:
    """Request-owned context for ``Component.prepare``."""

    deadline: float | None = None
    cancel_event: asyncio.Event | None = None
    partial_failure: PartialFailurePolicy = PartialFailurePolicy.FAIL_FAST
    cache: dict[str, Any] = field(default_factory=dict)
    timings: list[PrepareTiming] = field(default_factory=list)
    disconnect_capable: bool = False
    trace_span: Any | None = None
    # Injectable clock for ControllableClock / scenario tests (ASYNC-TEST-013).
    clock: Callable[[], float] = field(default_factory=lambda: time.monotonic)
    _cancelled: bool = field(default=False, init=False, repr=False)

    def remaining(self, *, now: float | None = None) -> float | None:
        if self.deadline is None:
            return None
        current = self.clock() if now is None else now
        return max(0.0, self.deadline - current)

    def is_cancelled(self) -> bool:
        if self._cancelled:
            return True
        if self.cancel_event is not None and self.cancel_event.is_set():
            self._cancelled = True
            return True
        remaining = self.remaining()
        if remaining is not None and remaining <= 0:
            self._cancelled = True
            return True
        return False

    def cancel(self) -> None:
        self._cancelled = True
        if self.cancel_event is not None:
            self.cancel_event.set()

    def check(self) -> None:
        if self.is_cancelled():
            raise error(
                "HED-PREPARE-0001",
                title="Prepare cancelled",
                explanation="Request-owned prepare work was cancelled by disconnect or deadline.",
                remediation="Shorten prepare work or raise deadlines; handle CancelledError.",
            )

    def cached(self, key: str, factory: Callable[[], T | Awaitable[T]]) -> Awaitable[T]:
        async def _resolve() -> T:
            self.check()
            if key in self.cache:
                return self.cache[key]  # type: ignore[no-any-return]
            value = factory()
            if inspect.isawaitable(value):
                value = await value  # type: ignore[assignment]
            self.cache[key] = value
            return value  # type: ignore[return-value]

        return _resolve()


def reset_prepare_for_tests() -> None:
    _active_prepare.set(None)


def collect_prepare_targets(
    value: NodeLike, *, _seen: set[int] | None = None
) -> list[Component[Any]]:
    """Depth-first collect components that define prepare()."""
    seen = _seen if _seen is not None else set()
    targets: list[Component[Any]] = []
    if isinstance(value, Component):
        obj_id = id(value)
        if obj_id in seen:
            return targets
        seen.add(obj_id)
        prepare_fn = type(value).prepare
        if prepare_fn is not Component.prepare:
            targets.append(value)
        children: Sequence[NodeLike] = getattr(value, "_children", ())
        for child in children:
            targets.extend(collect_prepare_targets(child, _seen=seen))
        slots: Mapping[str, NodeLike | list[NodeLike]] = getattr(value, "_slot_values", {})
        for slot_value in slots.values():
            if isinstance(slot_value, list):
                for item in slot_value:
                    targets.extend(collect_prepare_targets(item, _seen=seen))
            else:
                targets.extend(collect_prepare_targets(slot_value, _seen=seen))
        return targets
    if isinstance(value, (list, tuple)):
        for item in value:
            targets.extend(collect_prepare_targets(item, _seen=seen))
    return targets


async def prepare_tree(
    value: NodeLike,
    *,
    context: PrepareContext | None = None,
    concurrency_limit: int | None = None,
    run: Callable[[Awaitable[Any]], Awaitable[Any]] | None = None,
) -> PrepareContext:
    """Run optional prepare() hooks before sync render.

    Rendering remains synchronous and deterministic after this handoff.
    When ``run`` is provided (e.g. ``ConcurrencyLimiter.run``), each prepare
    body is driven through that runner instead of a local semaphore.
    """
    ctx = context or PrepareContext()
    token = _active_prepare.set(ctx)
    try:
        targets = collect_prepare_targets(value)
        if not targets:
            return ctx

        semaphore = (
            asyncio.Semaphore(concurrency_limit)
            if run is None and concurrency_limit is not None and concurrency_limit > 0
            else None
        )

        async def _run_one(component: Component[Any]) -> None:
            logical = component.logical_id()
            started = ctx.clock()
            cancelled = False
            err: str | None = None
            try:
                ctx.check()

                async def _body() -> None:
                    prepare = component.prepare
                    result = prepare(ctx)
                    if inspect.isawaitable(result):
                        await result

                async def _with_deadline() -> None:
                    remaining = ctx.remaining()
                    if remaining is not None:
                        try:
                            await asyncio.wait_for(_body(), timeout=remaining)
                        except TimeoutError as exc:
                            ctx.cancel()
                            raise error(
                                "HED-PREPARE-0002",
                                title="Prepare deadline exceeded",
                                explanation=(
                                    f"Prepare for {logical!r} exceeded the request deadline."
                                ),
                                remediation=(
                                    "Shorten prepare work or raise prepare_deadline_seconds."
                                ),
                            ) from exc
                    else:
                        await _body()

                if run is not None:
                    await run(_with_deadline())
                elif semaphore is not None:
                    async with semaphore:
                        await _with_deadline()
                else:
                    await _with_deadline()
            except asyncio.CancelledError:
                cancelled = True
                ctx.cancel()
                raise
            except Exception as exc:
                err = str(exc)
                if ctx.partial_failure is PartialFailurePolicy.FAIL_FAST:
                    raise
            finally:
                ctx.timings.append(
                    PrepareTiming(
                        logical_id=logical,
                        started_at=started,
                        finished_at=ctx.clock(),
                        cancelled=cancelled or ctx.is_cancelled(),
                        error=err,
                    )
                )

        if ctx.partial_failure is PartialFailurePolicy.CONTINUE:
            results = await asyncio.gather(
                *(_run_one(c) for c in targets),
                return_exceptions=True,
            )
            hard_errors = [
                r for r in results if isinstance(r, BaseException) and not isinstance(r, Exception)
            ]
            if hard_errors:
                raise hard_errors[0]
            return ctx

        await asyncio.gather(*(_run_one(c) for c in targets))
        return ctx
    finally:
        _active_prepare.reset(token)
