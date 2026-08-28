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
from typing import Any, ParamSpec, TypeVar

from edron.errors import BindingError
from hedron_core.cache.backend import validate_cache_ttl

P = ParamSpec("P")
R = TypeVar("R")


class CachedFunction:
    """A callable lowered to Hedron's native ``cache_data`` decorator."""

    def __init__(
        self,
        fn: Callable[..., Any],
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
        if not isinstance(version, str) or not version.strip():
            raise BindingError("cache version must be non-empty", code="EDRON_CACHE_VERSION")
        self.fn = fn
        self.ttl = ttl
        self.scope = scope
        self.max_entries = max_entries
        self.version = version
        self.tags = tuple(tags)
        self.vary_on = tuple(vary_on)
        self._identity = f"{fn.__module__}.{fn.__qualname__}"
        self._tag = f"edron:{self._identity}:{id(self)}"
        self._keys: OrderedDict[str, None] = OrderedDict()
        self._lock = RLock()

        from hedron.cache import cache_data as native_cache_data

        native = native_cache_data(
            ttl=ttl,
            scope=scope,
            version=version,
            tags=(*self.tags, self._tag),
            vary_on=self.vary_on,
        )(fn)
        self._native = native
        wraps(fn)(self)

    def _key(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
        from hedron_core.cache import build_cache_key

        bound: dict[str, Any] = {}
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

        with self._lock:
            self._keys[key] = None
            self._keys.move_to_end(key)
            while len(self._keys) > self.max_entries:
                evicted, _ = self._keys.popitem(last=False)
                get_cache_backend().invalidate(keys=(evicted,))

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        key = self._key(args, kwargs)
        result = self._native(*args, **kwargs)
        if inspect.isawaitable(result):

            async def await_result() -> Any:
                value = await result
                self._remember(key)
                return value

            return await_result()
        self._remember(key)
        return result

    def invalidate(self, *args: Any, **kwargs: Any) -> None:
        """Invalidate one invocation through the native cache backend."""
        from hedron_core.cache import get_cache_backend

        key = self._key(args, kwargs)
        get_cache_backend().invalidate(keys=(key,))
        with self._lock:
            self._keys.pop(key, None)

    def invalidate_all(self) -> None:
        """Invalidate all invocations of this callable."""
        from hedron_core.cache import invalidate_tags

        invalidate_tags(self._tag)
        with self._lock:
            self._keys.clear()


def cache_data(
    *,
    ttl: float | None = 60,
    scope: str = "private",
    max_entries: int = 128,
    version: str = "1",
    tags: tuple[str, ...] = (),
    vary_on: tuple[str, ...] = (),
) -> Callable[[Callable[P, R]], CachedFunction]:
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
