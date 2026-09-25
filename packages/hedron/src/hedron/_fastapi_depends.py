"""Typed FastAPI dependency factory used by the flagship package and Edron."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, cast


class _DependsFactory(Protocol):
    def __call__(
        self,
        dependency: Callable[..., object] | None = None,
        *,
        use_cache: bool = True,
        scope: str | None = None,
    ) -> object: ...


class _NoArgumentFactory(Protocol):
    def __call__(self) -> object: ...


def fastapi_depends(
    dependency: Callable[..., object] | None = None,
    *,
    use_cache: bool = True,
    scope: str | None = None,
) -> object:
    """Call FastAPI's dependency factory through an object-valued boundary."""
    from fastapi import Depends

    factory = cast(_DependsFactory, cast(object, Depends))
    return factory(dependency, use_cache=use_cache, scope=scope)


def fastapi_parameter(factory: object) -> object:
    """Call FastAPI's zero-argument parameter marker through a typed boundary."""
    return cast(_NoArgumentFactory, factory)()
