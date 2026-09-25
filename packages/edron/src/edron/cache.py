"""Native-backed bounded cache facade for Edron.

Edron deliberately does not maintain a second cache store.  The decorator below
adds only a small authoring wrapper around Hedron's cache policy, backend, tracing,
TTL, scope partitioning, and mutable-value isolation.
"""

from __future__ import annotations

import inspect
from collections import OrderedDict
from collections.abc import Callable
from functools import wraps
from threading import RLock
from typing import Generic, ParamSpec, TypeVar, cast

from edron.errors import BindingError
from hedron.cache.decorators import cache_callable_identity
from hedron_core.cache.backend import CacheBackend, validate_cache_ttl
from hedron_core.typing_support import awaitable_value

P = ParamSpec("P")
R = TypeVar("R")
_MAX_TRACKED_BACKENDS = 128


class CachedFunction(Generic[P, R]):
    """A callable lowered to Hedron's native ``cache_data`` decorator."""

    def __init__(
        self,
        fn: Callable[P, R],
        *,
        ttl: float | None = 60,
        scope: str = "private",
        max_entries: int = 128,
        version: str = "1",
        tags: tuple[str, ...] = (),
        vary_on: tuple[str, ...] = (),
    ) -> None:
        if not callable(fn):
            raise TypeError("cache_data expects a callable")
        ttl = validate_cache_ttl(ttl)
        if ttl is not None and ttl < 0:
            raise BindingError("cache ttl must be non-negative", code="EDRON_CACHE_TTL")
        if max_entries < 1:
            raise BindingError("cache max_entries must be positive", code="EDRON_CACHE_BOUNDS")
        raw_version: object = version
        if not isinstance(cast(object, raw_version), str) or not raw_version.strip():
            raise BindingError("cache version must be non-empty", code="EDRON_CACHE_VERSION")
        self.fn: Callable[P, R] = fn
        self.ttl = ttl
        self.scope = scope
        self.max_entries = max_entries
        self.version = version
        self.tags = tuple(tags)
        self.vary_on = tuple(vary_on)
        self._identity = cache_callable_identity(fn)
        self._tag = f"edron:{self._identity}:{id(self)}"
        # Retain the exact backend that owns each key. A CachedFunction may be
        # imported once and called by multiple application runtime contexts.
        self._keys: OrderedDict[int, tuple[CacheBackend, OrderedDict[str, None]]] = OrderedDict()
        self._lock = RLock()

        from hedron.cache import cache_data as native_cache_data

        native = native_cache_data(
            ttl=ttl,
            scope=scope,
            version=version,
            tags=(*self.tags, self._tag),
            vary_on=self.vary_on,
        )(fn)
        self._native: Callable[P, R] = native
        _ignored = wraps(fn)(self)

    def _key(self, args: tuple[object, ...], kwargs: dict[str, object]) -> str:
        from hedron_core.cache import build_cache_key

        bound: dict[str, object] = {}
        try:
            signature = inspect.signature(self.fn)
            bound_arguments = signature.bind_partial(*args, **kwargs)
            bound_arguments.apply_defaults()
            bound = dict(bound_arguments.arguments)
        except TypeError:
            bound = dict(kwargs)
        vary = {name: bound[name] for name in self.vary_on if name in bound}
        return build_cache_key(
            identity=self._identity,
            args=args,
            kwargs=kwargs,
            version=self.version,
            scope=self.scope,
            vary=vary,
        )

    def _remember(self, key: str) -> None:
        from hedron_core.cache import get_cache_backend

        backend = get_cache_backend()
        backend_id = id(backend)
        evicted_keys: list[str] = []
        evicted_backends: list[CacheBackend] = []
        with self._lock:
            record = self._keys.get(backend_id)
            if record is None or record[0] is not backend:
                entries: OrderedDict[str, None] = OrderedDict()
                self._keys[backend_id] = (backend, entries)
            else:
                entries = record[1]
            self._keys.move_to_end(backend_id)
            entries[key] = None
            entries.move_to_end(key)
            while len(entries) > self.max_entries:
                evicted_key, _ = entries.popitem(last=False)
                evicted_keys.append(evicted_key)
            while len(self._keys) > _MAX_TRACKED_BACKENDS:
                _, (old_backend, _) = self._keys.popitem(last=False)
                evicted_backends.append(old_backend)
        if evicted_keys:
            _ignored = backend.invalidate(keys=tuple(evicted_keys))
        for old_backend in evicted_backends:
            _ignored = old_backend.invalidate(tags=(self._tag,))

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        key = self._key(args, kwargs)
        result = self._native(*args, **kwargs)
        pending = awaitable_value(result)
        if pending is not None:

            async def await_result() -> object:
                value = await pending
                self._remember(key)
                return value

            # ``inspect.isawaitable`` establishes that R is awaitable at runtime,
            # but Python 3.10 typing cannot express that conditional relationship.
            return cast(R, await_result())
        self._remember(key)
        return result

    def invalidate(self, *args: object, **kwargs: object) -> None:
        """Invalidate one invocation through the native cache backend."""
        from hedron_core.cache import get_cache_backend

        key = self._key(args, kwargs)
        backend = get_cache_backend()
        _ignored = backend.invalidate(keys=(key,))
        with self._lock:
            record = self._keys.get(id(backend))
            if record is not None and record[0] is backend:
                record[1].pop(key, None)

    def invalidate_all(self) -> None:
        """Invalidate all invocations of this callable."""
        with self._lock:
            backends = {backend_id: record[0] for backend_id, record in self._keys.items()}
            self._keys.clear()
        # Invalidate every application backend this facade has populated, not
        # merely whichever ContextVar happens to be active at this call site.
        for backend in backends.values():
            _ignored = backend.invalidate(tags=(self._tag,))


def cache_data(
    *,
    ttl: float | None = 60,
    scope: str = "private",
    max_entries: int = 128,
    version: str = "1",
    tags: tuple[str, ...] = (),
    vary_on: tuple[str, ...] = (),
) -> Callable[[Callable[P, R]], CachedFunction[P, R]]:
    """Decorate a recomputable function with native TTL/scope/cache policy."""

    return lambda fn: CachedFunction(
        fn,
        ttl=ttl,
        scope=scope,
        max_entries=max_entries,
        version=version,
        tags=tags,
        vary_on=vary_on,
    )


__all__ = ["CachedFunction", "cache_data"]
