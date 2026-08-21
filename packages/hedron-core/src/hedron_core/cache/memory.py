"""Process-local in-memory cache backend."""

from __future__ import annotations

import asyncio
import inspect
import json
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar, cast

R = TypeVar("R")


class _AsyncSingleFlightRetry(Exception):
    """Owner cancelled; waiters should re-enter and take ownership."""


@dataclass
class _Entry:
    value: Any
    expires_at: float | None
    tags: tuple[str, ...]
    stored_at: float = field(default_factory=time.monotonic)
    size: int = 0


class InMemoryCacheBackend:
    process_local = True

    def __init__(self) -> None:
        self._store: dict[str, _Entry] = {}
        self._lock = threading.RLock()
        self._flights: dict[str, threading.Event] = {}
        self._flight_results: dict[str, object] = {}
        self._flight_errors: dict[str, BaseException] = {}
        self._flight_waiters: dict[str, int] = {}
        # Keyed by (cache key, event-loop id) so Futures are never shared across loops.
        self._async_flights: dict[tuple[str, int], asyncio.Future[Any]] = {}

    def get(self, key: str) -> Any | None:
        hit, value = self.lookup(key)
        return value if hit else None

    def lookup(self, key: str) -> tuple[bool, Any]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return False, None
            if entry.expires_at is not None and time.monotonic() >= entry.expires_at:
                del self._store[key]
                return False, None
            return True, entry.value

    def age_ms(self, key: str) -> float | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            return (time.monotonic() - entry.stored_at) * 1000

    def set(
        self,
        key: str,
        value: Any,
        *,
        ttl: float | None = None,
        tags: tuple[str, ...] = (),
    ) -> None:
        expires = None if ttl is None else time.monotonic() + ttl
        try:
            size = len(json.dumps(value, default=str))
        except TypeError:
            size = 0
        with self._lock:
            self._store[key] = _Entry(value=value, expires_at=expires, tags=tags, size=size)

    def invalidate(self, *, tags: tuple[str, ...] = (), keys: tuple[str, ...] = ()) -> int:
        removed = 0
        with self._lock:
            for key in keys:
                if self._store.pop(key, None) is not None:
                    removed += 1
            if tags:
                tagset = set(tags)
                for key, entry in list(self._store.items()):
                    if tagset.intersection(entry.tags):
                        del self._store[key]
                        removed += 1
        return removed

    def single_flight(self, key: str, loader: Callable[[], R]) -> R:
        with self._lock:
            hit, cached = self.lookup(key)
            if hit:
                return cast(R, cached)
            if key in self._flights:
                event = self._flights[key]
                self._flight_waiters[key] = self._flight_waiters.get(key, 0) + 1
                waiter = True
            else:
                event = threading.Event()
                self._flights[key] = event
                self._flight_waiters[key] = 0
                waiter = False
        if waiter:
            try:
                event.wait()
                if key in self._flight_errors:
                    raise self._flight_errors[key]
                return cast(R, self._flight_results[key])
            finally:
                with self._lock:
                    remaining = self._flight_waiters.get(key, 1) - 1
                    if remaining <= 0:
                        self._flight_waiters.pop(key, None)
                        self._flight_results.pop(key, None)
                        self._flight_errors.pop(key, None)
                    else:
                        self._flight_waiters[key] = remaining
        try:
            value = loader()
            self._flight_results[key] = value
            return value
        except BaseException as exc:
            self._flight_errors[key] = exc
            raise
        finally:
            with self._lock:
                event.set()
                self._flights.pop(key, None)
                # Owner keeps results until waiters drain (or none were registered).
                if self._flight_waiters.get(key, 0) <= 0:
                    self._flight_waiters.pop(key, None)
                    self._flight_results.pop(key, None)
                    self._flight_errors.pop(key, None)

    async def single_flight_async(self, key: str, loader: Callable[[], Any]) -> Any:
        while True:
            hit, cached = self.lookup(key)
            if hit:
                return cached
            loop = asyncio.get_running_loop()
            flight_key = (key, id(loop))
            with self._lock:
                existing = self._async_flights.get(flight_key)
                if existing is not None:
                    fut = existing
                    owner = False
                else:
                    fut = loop.create_future()
                    self._async_flights[flight_key] = fut
                    owner = True
            if not owner:
                try:
                    return await asyncio.shield(fut)
                except _AsyncSingleFlightRetry:
                    # Owner cancelled; try again as a new owner or waiter.
                    continue
            try:
                result = loader()
                if inspect.isawaitable(result):
                    result = await result
                if not fut.done():
                    fut.set_result(result)
                return result
            except asyncio.CancelledError:
                # Do not publish CancelledError into the shared future — that
                # would cancel sibling waiters that were not themselves cancelled.
                with self._lock:
                    if self._async_flights.get(flight_key) is fut:
                        self._async_flights.pop(flight_key, None)
                if not fut.done():
                    fut.set_exception(_AsyncSingleFlightRetry())
                raise
            except BaseException as exc:
                if not fut.done():
                    fut.set_exception(exc)
                raise
            finally:
                with self._lock:
                    if self._async_flights.get(flight_key) is fut:
                        self._async_flights.pop(flight_key, None)
