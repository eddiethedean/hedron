"""Optional component prepare() lifecycle (phase 0.13)."""

from __future__ import annotations

import asyncio
import inspect
import time
from collections.abc import Awaitable, Callable, Sequence
from contextlib import suppress
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import TypeVar, cast

from hedron_core.compat import StrEnum
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error
from hedron_core.html import NativeElement
from hedron_core.models import Props

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
    cache: dict[str, object] = field(default_factory=dict[str, object])
    timings: list[PrepareTiming] = field(default_factory=list[PrepareTiming])
    disconnect_capable: bool = False
    trace_span: object | None = None
    # Injectable clock for ControllableClock / scenario tests (ASYNC-TEST-013).
    clock: Callable[[], float] = field(default_factory=lambda: time.monotonic)
    _cancelled: bool = field(default=False, init=False, repr=False)
    _inflight: dict[str, asyncio.Future[object]] = field(
        default_factory=dict[str, asyncio.Future[object]], init=False, repr=False
    )

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
                return cast(T, self.cache[key])
            loop = asyncio.get_running_loop()
            fut: asyncio.Future[object] = loop.create_future()
            existing = self._inflight.setdefault(key, fut)
            if existing is not fut:
                return cast(T, await asyncio.shield(existing))
            try:
                produced = factory()
                value = await produced if inspect.isawaitable(produced) else produced
                self.cache[key] = value
                if not fut.done():
                    fut.set_result(value)
                return cast(T, value)
            except BaseException as exc:
                if not fut.done():
                    fut.set_exception(exc)
                    # The owner raises directly. Mark the shared Future's
                    # exception observed so owner-only failures do not emit
                    # "Future exception was never retrieved" at GC time.
                    with suppress(BaseException):
                        fut.exception()
                raise
            finally:
                if self._inflight.get(key) is fut:
                    self._inflight.pop(key, None)

        return _resolve()


def reset_prepare_for_tests() -> None:
    _active_prepare.set(None)


def collect_prepare_targets(
    value: object, *, _seen: set[int] | None = None
) -> list[Component[Props]]:
    """Depth-first collect components that define prepare()."""
    seen = _seen if _seen is not None else set[int]()
    targets: list[Component[Props]] = []
    # Use an explicit stack: deeply nested trees must reach the renderer's
    # bounded-depth diagnostic instead of exhausting Python's call stack here.
    stack: list[object] = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, Component):
            component = cast(Component[Props], current)
            obj_id = id(component)
            if obj_id in seen:
                continue
            seen.add(obj_id)
            if component.has_prepare_override():
                targets.append(component)
            children: list[object] = list(component.child_nodes)
            for slot_value in component.slot_values.values():
                if isinstance(slot_value, list):
                    children.extend(slot_value)
                else:
                    children.append(slot_value)
            stack.extend(reversed(children))
            continue
        if isinstance(current, Sequence) and not isinstance(current, (str, bytes)):
            obj_id = id(current)
            if obj_id in seen:
                continue
            seen.add(obj_id)
            stack.extend(reversed(cast(Sequence[object], current)))
            continue
        if isinstance(current, NativeElement):
            obj_id = id(current)
            if obj_id in seen:
                continue
            seen.add(obj_id)
            stack.extend(reversed(current.children))
    return targets


async def prepare_tree(
    value: NodeLike,
    *,
    context: PrepareContext | None = None,
    concurrency_limit: int | None = None,
    run: Callable[[Awaitable[object]], Awaitable[object]] | None = None,
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

        async def _run_one(component: Component[Props]) -> None:
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
                        except asyncio.TimeoutError as exc:
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

        tasks = [asyncio.create_task(_run_one(component)) for component in targets]
        try:
            await asyncio.gather(*tasks)
        except BaseException:
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            raise
        return ctx
    finally:
        _active_prepare.reset(token)
