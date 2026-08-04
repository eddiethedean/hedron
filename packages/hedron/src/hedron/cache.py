"""Public cache_data / cache_component decorators."""

from __future__ import annotations

import functools
import inspect
import time
from collections.abc import Callable, Mapping
from typing import Any, ParamSpec, TypeVar, overload

from hedron_core.cache import (
    CacheEvent,
    CacheScope,
    InMemoryCacheBackend,
    build_cache_key,
    get_cache_backend,
    record_cache_trace,
)

P = ParamSpec("P")
R = TypeVar("R")

__all__ = ["cache_component", "cache_data", "htmx_vary_dimensions"]


def htmx_vary_dimensions(*, vary_on_target: bool = False) -> tuple[str, ...]:
    """Cache/response dimensions that separate pages from HTMX fragments."""
    dims = ("HX-Request", "HX-History-Restore-Request")
    if vary_on_target:
        return (*dims, "HX-Target")
    return dims


def _identity_for(fn: Callable[..., Any]) -> str:
    return f"{fn.__module__}.{fn.__qualname__}"


def _bound_arguments(
    fn: Callable[..., Any], args: tuple[Any, ...], kwargs: Mapping[str, Any]
) -> dict[str, Any]:
    try:
        bound = inspect.signature(fn).bind_partial(*args, **dict(kwargs))
        bound.apply_defaults()
        return dict(bound.arguments)
    except TypeError:
        return dict(kwargs)


def _vary_from_kwargs(kwargs: Mapping[str, Any], vary_on: tuple[str, ...]) -> dict[str, Any]:
    missing = [k for k in vary_on if k not in kwargs]
    if missing:
        raise KeyError(f"missing vary_on keys: {', '.join(missing)}")
    return {k: kwargs[k] for k in vary_on}


_SENSITIVE_SCOPES = frozenset(
    {
        CacheScope.PRIVATE.value,
        CacheScope.USER.value,
        CacheScope.TENANT.value,
        CacheScope.SESSION.value,
    }
)
_PUBLIC_SENSITIVE_NAMES = frozenset(
    {"user", "user_id", "request", "session", "tenant", "tenant_id"}
)


def _should_reject_cache(
    *,
    scope: str,
    args: tuple[Any, ...],
    kwargs: Mapping[str, Any],
    vary_on: tuple[str, ...],
    bound: Mapping[str, Any] | None = None,
) -> str | None:
    if scope in _SENSITIVE_SCOPES and not vary_on:
        return f"scope {scope!r} requires vary_on dimensions"
    if scope in _SENSITIVE_SCOPES and vary_on:
        source = bound if bound is not None else kwargs
        missing = [k for k in vary_on if k not in source or source[k] is None]
        if missing:
            return f"scope {scope!r} missing vary_on values: {', '.join(missing)}"
    if scope == CacheScope.PUBLIC.value:
        if any(k in _PUBLIC_SENSITIVE_NAMES for k in kwargs):
            return "user-specific kwargs under public scope"
        # Positional request-like objects must not be cached publicly.
        for arg in args:
            type_name = type(arg).__name__
            if type_name in {"Request", "HTTPConnection"} or "Session" in type_name:
                return "request/session positional arg under public scope"
    return None


def _decorate(
    fn: Callable[P, R],
    *,
    ttl: float | None,
    scope: str,
    version: str,
    tags: tuple[str, ...],
    vary_on: tuple[str, ...],
    component: bool,
) -> Callable[P, R]:
    del component  # reserved for future prepared-component policy hooks
    identity = _identity_for(fn)
    is_async = inspect.iscoroutinefunction(fn)

    if is_async:

        @functools.wraps(fn)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            bound = _bound_arguments(fn, args, kwargs)
            reject = _should_reject_cache(
                scope=scope, args=args, kwargs=kwargs, vary_on=vary_on, bound=bound
            )
            if reject:
                record_cache_trace(
                    CacheEvent(
                        kind="reject",
                        key_fingerprint=identity,
                        scope=scope,
                        detail=reject,
                    )
                )
                return await fn(*args, **kwargs)  # type: ignore[misc]
            key = build_cache_key(
                identity=identity,
                args=args,
                kwargs=kwargs,
                version=version,
                scope=scope,
                vary=_vary_from_kwargs(bound, vary_on) if vary_on else {},
            )
            backend = get_cache_backend()
            cached = backend.get(key)
            if cached is not None:
                age = None
                if isinstance(backend, InMemoryCacheBackend):
                    age = backend.age_ms(key)
                record_cache_trace(
                    CacheEvent(kind="hit", key_fingerprint=key, scope=scope, age_ms=age)
                )
                return cached  # type: ignore[return-value]
            record_cache_trace(CacheEvent(kind="miss", key_fingerprint=key, scope=scope))

            async def loader() -> R:
                return await fn(*args, **kwargs)  # type: ignore[misc]

            if isinstance(backend, InMemoryCacheBackend):
                started = time.monotonic()
                try:
                    value = await backend.single_flight_async(key, loader)
                except Exception:
                    raise
                backend.set(key, value, ttl=ttl, tags=tags)
                record_cache_trace(
                    CacheEvent(
                        kind="store",
                        key_fingerprint=key,
                        scope=scope,
                        age_ms=(time.monotonic() - started) * 1000,
                        tags=tags,
                    )
                )
                return value  # type: ignore[return-value]
            value = await loader()
            backend.set(key, value, ttl=ttl, tags=tags)
            return value

        return async_wrapper  # type: ignore[return-value]

    @functools.wraps(fn)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        bound = _bound_arguments(fn, args, kwargs)
        reject = _should_reject_cache(
            scope=scope, args=args, kwargs=kwargs, vary_on=vary_on, bound=bound
        )
        if reject:
            record_cache_trace(
                CacheEvent(
                    kind="reject",
                    key_fingerprint=identity,
                    scope=scope,
                    detail=reject,
                )
            )
            return fn(*args, **kwargs)
        key = build_cache_key(
            identity=identity,
            args=args,
            kwargs=kwargs,
            version=version,
            scope=scope,
            vary=_vary_from_kwargs(bound, vary_on) if vary_on else {},
        )
        backend = get_cache_backend()
        cached = backend.get(key)
        if cached is not None:
            age = backend.age_ms(key) if isinstance(backend, InMemoryCacheBackend) else None
            record_cache_trace(CacheEvent(kind="hit", key_fingerprint=key, scope=scope, age_ms=age))
            return cached  # type: ignore[return-value]
        record_cache_trace(CacheEvent(kind="miss", key_fingerprint=key, scope=scope))

        def loader() -> R:
            return fn(*args, **kwargs)

        if isinstance(backend, InMemoryCacheBackend):
            try:
                value = backend.single_flight(key, loader)
            except Exception:
                raise
            backend.set(key, value, ttl=ttl, tags=tags)
            record_cache_trace(
                CacheEvent(kind="store", key_fingerprint=key, scope=scope, tags=tags)
            )
            return value
        value = loader()
        backend.set(key, value, ttl=ttl, tags=tags)
        return value

    return sync_wrapper  # type: ignore[return-value]


@overload
def cache_data(
    fn: Callable[P, R],
    /,
) -> Callable[P, R]: ...


@overload
def cache_data(
    *,
    ttl: float | None = 60,
    scope: str = "private",
    version: str = "1",
    tags: tuple[str, ...] = (),
    vary_on: tuple[str, ...] = (),
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


def cache_data(
    fn: Callable[P, R] | None = None,
    /,
    *,
    ttl: float | None = 60,
    scope: str = "private",
    version: str = "1",
    tags: tuple[str, ...] = (),
    vary_on: tuple[str, ...] = (),
) -> Any:
    def decorator(f: Callable[P, R]) -> Callable[P, R]:
        return _decorate(
            f,
            ttl=ttl,
            scope=scope,
            version=version,
            tags=tags,
            vary_on=vary_on,
            component=False,
        )

    if fn is not None:
        return decorator(fn)
    return decorator


@overload
def cache_component(
    fn: Callable[P, R],
    /,
) -> Callable[P, R]: ...


@overload
def cache_component(
    *,
    ttl: float | None = 30,
    scope: str = "private",
    version: str = "1",
    tags: tuple[str, ...] = (),
    vary_on: tuple[str, ...] = (),
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


def cache_component(
    fn: Callable[P, R] | None = None,
    /,
    *,
    ttl: float | None = 30,
    scope: str = "private",
    version: str = "1",
    tags: tuple[str, ...] = (),
    vary_on: tuple[str, ...] = (),
) -> Any:
    def decorator(f: Callable[P, R]) -> Callable[P, R]:
        return _decorate(
            f,
            ttl=ttl,
            scope=scope,
            version=version,
            tags=tags,
            vary_on=vary_on,
            component=True,
        )

    if fn is not None:
        return decorator(fn)
    return decorator
