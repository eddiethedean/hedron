"""Cache protocols, keying, single-flight, and in-memory backend."""

from __future__ import annotations

import asyncio
import hashlib
import inspect
import json
import threading
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, ParamSpec, TypeVar

from hedron_core.security import Secret

P = ParamSpec("P")
R = TypeVar("R")

__all__ = [
    "CacheBackend",
    "CacheEvent",
    "CacheScope",
    "CacheTrace",
    "InMemoryCacheBackend",
    "build_cache_key",
    "get_cache_backend",
    "get_cache_traces",
    "invalidate_tags",
    "record_cache_trace",
    "reset_cache_for_tests",
    "set_cache_backend",
]


class CacheScope(StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    USER = "user"
    TENANT = "tenant"
    SESSION = "session"


@dataclass(frozen=True, slots=True)
class CacheEvent:
    kind: str  # hit|miss|wait|store|reject|invalidate
    key_fingerprint: str
    scope: str
    age_ms: float | None = None
    size: int | None = None
    tags: tuple[str, ...] = ()
    detail: str = ""


_traces: list[CacheEvent] = []
_TRACE_LIMIT = 200


def record_cache_trace(event: CacheEvent) -> None:
    _traces.append(event)
    if len(_traces) > _TRACE_LIMIT:
        del _traces[: len(_traces) - _TRACE_LIMIT]


def get_cache_traces() -> tuple[CacheEvent, ...]:
    return tuple(_traces)


class CacheTrace:
    """Explorer-facing snapshot of recent cache activity."""

    @staticmethod
    def recent(limit: int = 50) -> list[dict[str, Any]]:
        events = list(_traces)[-limit:]
        return [
            {
                "kind": e.kind,
                "key_fingerprint": e.key_fingerprint,
                "scope": e.scope,
                "age_ms": e.age_ms,
                "size": e.size,
                "tags": list(e.tags),
                "detail": e.detail,
            }
            for e in events
        ]


def _fingerprint(material: str) -> str:
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]


def _normalize_arg(value: Any) -> Any:
    if isinstance(value, Secret):
        # Non-reversible keyed transform — never store plaintext secret in key material.
        return {"__secret__": _fingerprint(repr(value.reveal()))}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, Mapping):
        return {
            str(k): _normalize_arg(v)
            for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))  # type: ignore[misc]
        }
    if isinstance(value, (list, tuple)):
        return [_normalize_arg(v) for v in value]
    # Request/dependency objects must never be serialized.
    type_name = type(value).__name__
    if type_name in {"Request", "HTTPConnection"} or "Dependency" in type_name:
        raise ValueError(f"Cannot use {type_name} as a cache key argument")
    if hasattr(value, "model_dump"):
        return _normalize_arg(value.model_dump())
    return repr(value)


def build_cache_key(
    *,
    identity: str,
    args: tuple[Any, ...] = (),
    kwargs: Mapping[str, Any] | None = None,
    version: str = "1",
    scope: str = CacheScope.PRIVATE.value,
    vary: Mapping[str, Any] | None = None,
) -> str:
    payload = {
        "identity": identity,
        "version": version,
        "scope": scope,
        "args": [_normalize_arg(a) for a in args],
        "kwargs": {k: _normalize_arg(v) for k, v in sorted((kwargs or {}).items())},
        "vary": {k: _normalize_arg(v) for k, v in sorted((vary or {}).items())},
    }
    material = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return _fingerprint(material)


class CacheBackend:
    def get(self, key: str) -> Any | None:  # pragma: no cover - protocol
        raise NotImplementedError

    def set(
        self,
        key: str,
        value: Any,
        *,
        ttl: float | None = None,
        tags: tuple[str, ...] = (),
    ) -> None:  # pragma: no cover
        raise NotImplementedError

    def invalidate(self, *, tags: tuple[str, ...] = (), keys: tuple[str, ...] = ()) -> int:
        raise NotImplementedError


@dataclass
class _Entry:
    value: Any
    expires_at: float | None
    tags: tuple[str, ...]
    stored_at: float = field(default_factory=time.monotonic)
    size: int = 0


class InMemoryCacheBackend(CacheBackend):
    def __init__(self) -> None:
        self._store: dict[str, _Entry] = {}
        self._lock = threading.RLock()
        self._flights: dict[str, threading.Event] = {}
        self._flight_results: dict[str, Any] = {}
        self._flight_errors: dict[str, BaseException] = {}
        self._flight_waiters: dict[str, int] = {}
        self._async_flights: dict[str, asyncio.Future[Any]] = {}

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if entry.expires_at is not None and time.monotonic() >= entry.expires_at:
                del self._store[key]
                return None
            return entry.value

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
            cached = self.get(key)
            if cached is not None:
                return cached  # type: ignore[return-value]
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
                return self._flight_results[key]  # type: ignore[return-value]
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
        cached = self.get(key)
        if cached is not None:
            return cached
        loop = asyncio.get_running_loop()
        with self._lock:
            existing = self._async_flights.get(key)
            if existing is not None:
                fut = existing
                owner = False
            else:
                fut = loop.create_future()
                self._async_flights[key] = fut
                owner = True
        if not owner:
            return await asyncio.shield(fut)
        try:
            result = loader()
            if inspect.isawaitable(result):
                result = await result
            if not fut.done():
                fut.set_result(result)
            return result
        except BaseException as exc:
            if not fut.done():
                fut.set_exception(exc)
            raise
        finally:
            with self._lock:
                self._async_flights.pop(key, None)


_backend: CacheBackend = InMemoryCacheBackend()


def get_cache_backend() -> CacheBackend:
    return _backend


def set_cache_backend(backend: CacheBackend) -> None:
    global _backend
    _backend = backend


def invalidate_tags(*tags: str) -> int:
    count = get_cache_backend().invalidate(tags=tags)
    record_cache_trace(
        CacheEvent(
            kind="invalidate",
            key_fingerprint="*",
            scope="*",
            tags=tags,
            detail=f"removed={count}",
        )
    )
    return count


def reset_cache_for_tests() -> None:
    global _backend
    _backend = InMemoryCacheBackend()
    _traces.clear()
