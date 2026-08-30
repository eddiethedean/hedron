"""Deterministic async scenario test utilities (phase 0.13)."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, TypeVar

__all__ = [
    "AsyncScenario",
    "ControllableClock",
    "ScriptedDependency",
    "assert_ordered_events",
    "scripted_outcome",
]

T = TypeVar("T")


@dataclass
class ControllableClock:
    """Monotonic clock for deadline tests without wall-clock sleeps."""

    now: float = 0.0

    def advance(self, seconds: float) -> float:
        self.now += max(0.0, seconds)
        return self.now

    def monotonic(self) -> float:
        return self.now


@dataclass
class ScriptedDependency:
    """Scripted dependency outcome for prepare/job scenarios."""

    name: str
    outcome: str = "success"  # success | fail | hang_until_cancel
    value: Any = None
    error: Exception | None = None
    events: list[str] = field(default_factory=list[str])

    async def run(self, *, cancel_event: asyncio.Event | None = None) -> Any:
        self.events.append(f"{self.name}:start")
        if self.outcome == "fail":
            self.events.append(f"{self.name}:fail")
            raise self.error or RuntimeError(f"{self.name} failed")
        if self.outcome == "hang_until_cancel":
            if cancel_event is None:
                cancel_event = asyncio.Event()
            await cancel_event.wait()
            self.events.append(f"{self.name}:cancelled")
            raise asyncio.CancelledError()
        self.events.append(f"{self.name}:success")
        return self.value


def scripted_outcome(
    name: str,
    *,
    outcome: str = "success",
    value: Any = None,
    error: Exception | None = None,
) -> ScriptedDependency:
    return ScriptedDependency(name=name, outcome=outcome, value=value, error=error)


@dataclass
class AsyncScenario:
    """Ordered event recorder for prepare/cancel/disconnect scenarios."""

    clock: ControllableClock = field(default_factory=ControllableClock)
    events: list[str] = field(default_factory=list[str])
    cancel_event: asyncio.Event = field(default_factory=asyncio.Event)

    def record(self, event: str) -> None:
        self.events.append(event)

    def trigger_cancel(self) -> None:
        self.record("cancel")
        self.cancel_event.set()

    def trigger_disconnect(self) -> None:
        self.record("disconnect")
        self.cancel_event.set()

    async def run(self, coro: Awaitable[T] | Callable[[], Awaitable[T]]) -> T:
        self.record("scenario:start")
        try:
            if callable(coro) and not asyncio.iscoroutine(coro):
                result = await coro()  # type: ignore[misc]
            else:
                result = await coro  # type: ignore[misc]
            self.record("scenario:success")
            return result  # type: ignore[no-any-return]
        except asyncio.CancelledError:
            self.record("scenario:cancelled")
            raise
        except Exception:
            self.record("scenario:error")
            raise


def assert_ordered_events(actual: Sequence[str], expected: Sequence[str]) -> None:
    """Assert expected events appear in order (not necessarily contiguous)."""
    idx = 0
    for event in expected:
        while idx < len(actual) and actual[idx] != event:
            idx += 1
        assert idx < len(actual), f"missing ordered event {event!r} in {list(actual)!r}"
        idx += 1
