"""Adaptive concurrency controls (phase 0.13)."""

from __future__ import annotations

import asyncio
import contextlib
import math
from collections.abc import Awaitable
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any

from hedron_core.diagnostics import HedronError, error

__all__ = [
    "ConcurrencyConfig",
    "ConcurrencyLimiter",
    "adaptive_gather",
    "configure_concurrency",
    "get_concurrency_config",
    "reset_concurrency_for_tests",
]

_config: ContextVar[ConcurrencyConfig | None] = ContextVar(
    "hedron_concurrency_config", default=None
)
_global: ConcurrencyConfig | None = None


@dataclass(slots=True)
class ConcurrencyConfig:
    """Capacity-driven limits. Disable without changing component semantics."""

    enabled: bool = True
    max_in_flight: int = 32
    degrade_at: int = 24
    prepare_deadline_seconds: float | None = None

    def __post_init__(self) -> None:
        if self.max_in_flight < 1:
            raise ValueError("max_in_flight must be at least 1")
        if self.degrade_at < 1:
            raise ValueError("degrade_at must be at least 1")
        if self.prepare_deadline_seconds is not None and (
            not math.isfinite(self.prepare_deadline_seconds) or self.prepare_deadline_seconds <= 0
        ):
            raise ValueError("prepare_deadline_seconds must be a finite positive number")


class ConcurrencyLimiter:
    def __init__(self, config: ConcurrencyConfig) -> None:
        self.config = config
        self._sem = asyncio.Semaphore(max(1, config.max_in_flight))
        self._in_flight = 0
        self._overload_count = 0
        self._lock = asyncio.Lock()

    @property
    def in_flight(self) -> int:
        return self._in_flight

    @property
    def overload_count(self) -> int:
        return self._overload_count

    async def run(self, awaitable: Awaitable[Any]) -> Any:
        if not self.config.enabled:
            return await awaitable
        async with self._lock:
            # Shed at degrade_at (not only at hard max_in_flight).
            if self._in_flight >= self.config.degrade_at:
                self._overload_count += 1
                close = getattr(awaitable, "close", None)
                if callable(close):
                    close()
                raise error(
                    "HED-CONC-0001",
                    title="Concurrency capacity exceeded",
                    explanation=(
                        f"Adaptive concurrency shed work at degrade_at ({self.config.degrade_at})."
                    ),
                    remediation=(
                        "Reduce parallel work, raise degrade_at/max_in_flight, "
                        "or disable adaptive concurrency."
                    ),
                )
            if self._in_flight >= self.config.max_in_flight:
                self._overload_count += 1
                close = getattr(awaitable, "close", None)
                if callable(close):
                    close()
                raise error(
                    "HED-CONC-0001",
                    title="Concurrency capacity exceeded",
                    explanation=(
                        "Adaptive concurrency refused additional in-flight prepare/gather work."
                    ),
                    remediation=(
                        "Reduce parallel work, raise max_in_flight, "
                        "or disable adaptive concurrency."
                    ),
                )
            self._in_flight += 1
        try:
            async with self._sem:
                return await awaitable
        finally:
            async with self._lock:
                self._in_flight = max(0, self._in_flight - 1)


_limiter: ConcurrencyLimiter | None = None


def get_concurrency_config() -> ConcurrencyConfig:
    current = _config.get()
    if current is not None:
        return current
    return _global or ConcurrencyConfig()


def configure_concurrency(
    *,
    enabled: bool = True,
    max_in_flight: int = 32,
    degrade_at: int = 24,
    prepare_deadline_seconds: float | None = None,
) -> ConcurrencyConfig:
    global _global, _limiter
    cfg = ConcurrencyConfig(
        enabled=enabled,
        max_in_flight=max_in_flight,
        degrade_at=degrade_at,
        prepare_deadline_seconds=prepare_deadline_seconds,
    )
    _global = cfg
    _limiter = ConcurrencyLimiter(cfg)
    return cfg


def reset_concurrency_for_tests() -> None:
    global _global, _limiter
    _global = None
    _limiter = None
    _config.set(None)


def get_limiter() -> ConcurrencyLimiter:
    """Return the process-wide concurrency limiter, creating it on first use."""
    global _limiter
    if _limiter is None:
        _limiter = ConcurrencyLimiter(get_concurrency_config())
    return _limiter


# Retain the established private import for compatibility.
_get_limiter = get_limiter


async def adaptive_gather(
    *aws: Awaitable[Any],
    return_exceptions: bool = False,
) -> list[Any]:
    """Gather with capacity limits when adaptive concurrency is enabled."""
    if not aws:
        return []
    limiter = get_limiter()
    if not limiter.config.enabled:
        tasks = [asyncio.ensure_future(awaitable) for awaitable in aws]
        try:
            return list(await asyncio.gather(*tasks, return_exceptions=return_exceptions))
        except BaseException:
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            raise

    overload_event = asyncio.Event()

    async def _cancel_siblings_on_overload() -> None:
        await overload_event.wait()
        for task in tasks:
            if not task.done():
                task.cancel()

    async def _wrapped(aw: Awaitable[Any]) -> Any:
        try:
            return await limiter.run(aw)
        except HedronError as exc:
            if exc.diagnostic.code == "HED-CONC-0001":
                overload_event.set()
            raise

    tasks = [asyncio.create_task(_wrapped(aw)) for aw in aws]
    cancel_task = asyncio.create_task(_cancel_siblings_on_overload())
    try:
        return list(await asyncio.gather(*tasks, return_exceptions=return_exceptions))
    except BaseException:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise
    finally:
        cancel_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await cancel_task
