"""cache_data / cache_component decorator implementation."""

from __future__ import annotations

import functools
import inspect
import time
from collections.abc import Awaitable, Callable, Mapping
from typing import ParamSpec, TypeVar, cast, overload

from hedron.cache.policy import should_reject_cache
from hedron_core.cache import (
    CacheEvent,
    InMemoryCacheBackend,
    build_cache_key,
    get_cache_backend,
    record_cache_trace,
)
from hedron_core.cache.backend import validate_cache_ttl

P = ParamSpec("P")
R = TypeVar("R")

__all__ = ["cache_component", "cache_data"]


def _identity_for(fn: Callable[..., object]) -> str:
    return f"{fn.__module__}.{fn.__qualname__}"


def _bound_arguments(
    fn: Callable[..., object], args: tuple[object, ...], kwargs: Mapping[str, object]
) -> dict[str, object]:
    try:
        bound = inspect.signature(fn).bind_partial(*args, **dict(kwargs))
        bound.apply_defaults()
        return dict(bound.arguments)
    except TypeError:
        return dict(kwargs)


def _vary_from_kwargs(kwargs: Mapping[str, object], vary_on: tuple[str, ...]) -> dict[str, object]:
    missing = [k for k in vary_on if k not in kwargs]
    if missing:
        raise KeyError(f"missing vary_on keys: {', '.join(missing)}")
    return {k: kwargs[k] for k in vary_on}


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
    ttl = validate_cache_ttl(ttl)
    identity = _identity_for(fn)
    is_async = inspect.iscoroutinefunction(fn)

    if is_async:
        # iscoroutinefunction narrows runtime, not ParamSpec R; awaitable form is local.
        async_fn = cast(Callable[P, Awaitable[R]], fn)

        @functools.wraps(fn)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            bound = _bound_arguments(fn, args, kwargs)
            reject = should_reject_cache(
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
                return await async_fn(*args, **kwargs)
            key = build_cache_key(
                identity=identity,
                args=args,
                kwargs=kwargs,
                version=version,
                scope=scope,
                vary=_vary_from_kwargs(bound, vary_on) if vary_on else {},
            )
            backend = get_cache_backend()
            hit, cached = backend.lookup(key)
            if hit:
                age = None
                if isinstance(backend, InMemoryCacheBackend):
                    age = backend.age_ms(key)
                record_cache_trace(
                    CacheEvent(kind="hit", key_fingerprint=key, scope=scope, age_ms=age)
                )
                return cast(R, cached)
            record_cache_trace(CacheEvent(kind="miss", key_fingerprint=key, scope=scope))

            async def loader() -> R:
                return await async_fn(*args, **kwargs)

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
                return cast(R, value)
            value = await loader()
            backend.set(key, value, ttl=ttl, tags=tags)
            return value

        return cast(Callable[P, R], async_wrapper)

    @functools.wraps(fn)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        bound = _bound_arguments(fn, args, kwargs)
        reject = should_reject_cache(
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
        hit, cached = backend.lookup(key)
        if hit:
            age = backend.age_ms(key) if isinstance(backend, InMemoryCacheBackend) else None
            record_cache_trace(CacheEvent(kind="hit", key_fingerprint=key, scope=scope, age_ms=age))
            return cast(R, cached)
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

    return sync_wrapper


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
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
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
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
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
