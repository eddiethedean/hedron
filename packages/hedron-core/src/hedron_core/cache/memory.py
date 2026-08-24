"""Process-local in-memory cache backend."""

from __future__ import annotations

import asyncio
import copy
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


@dataclass
class _SyncFlight:
    """Per-generation single-flight state shared by owner and waiters (#576)."""

    event: threading.Event = field(default_factory=threading.Event)
    waiters: int = 0
    result: object | None = None
    error: BaseException | None = None
    has_result: bool = False


class InMemoryCacheBackend:
    process_local = True

    def __init__(self) -> None:
        self._store: dict[str, _Entry] = {}
        self._lock = threading.RLock()
        self._flights: dict[str, _SyncFlight] = {}
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
            return True, copy.deepcopy(entry.value)

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
            self._store[key] = _Entry(
                value=copy.deepcopy(value), expires_at=expires, tags=tags, size=size
            )

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
            flight = self._flights.get(key)
            if flight is not None:
                flight.waiters += 1
                waiter = True
            else:
                flight = _SyncFlight()
                self._flights[key] = flight
                waiter = False
        if waiter:
            try:
                flight.event.wait()
                if flight.error is not None:
                    raise flight.error
                if not flight.has_result:
                    raise KeyError(key)
                return cast(R, flight.result)
            finally:
                with self._lock:
                    flight.waiters -= 1
        try:
            value = loader()
            flight.result = value
            flight.has_result = True
            return value
        except BaseException as exc:
            flight.error = exc
            raise
        finally:
            with self._lock:
                flight.event.set()
                # Drop the map entry so a new generation gets its own _SyncFlight.
                if self._flights.get(key) is flight:
                    self._flights.pop(key, None)

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
