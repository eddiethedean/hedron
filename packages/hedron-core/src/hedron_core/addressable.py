"""Framework-neutral addressable component descriptors."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Generic, ParamSpec, TypeVar, overload

from hedron_core.identifiers import component_type_id, registry_resource_id
from hedron_core.registry import register_addressable

__all__ = ["AddressableDescriptor", "addressable"]

P = ParamSpec("P")
R = TypeVar("R")


@dataclass(frozen=True, slots=True)
class AddressableDescriptor(Generic[P, R]):
    """Reusable typed resource descriptor; not HTTP-reachable until exposed."""

    factory: Callable[P, R]
    logical_id: str
    name: str
    module: str
    distribution: str = "hedron-core"
    methods: tuple[str, ...] = ("GET",)
    include_in_schema: bool = False
    cache_private: bool = True
    tags: tuple[str, ...] = ()
    docs: str | None = None
    extras: dict[str, object] = field(default_factory=dict[str, object])

    @property
    def registry_key(self) -> str:
        return registry_resource_id("addressable", self.logical_id)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self.factory(*args, **kwargs)

    @property
    def __name__(self) -> str:
        return self.name

    @property
    def __wrapped__(self) -> Callable[P, R]:
        return self.factory


@overload
def addressable(factory: Callable[P, R], /) -> AddressableDescriptor[P, R]: ...


@overload
def addressable(
    *,
    name: str | None = None,
    distribution: str = "hedron-core",
    methods: tuple[str, ...] = ("GET",),
    include_in_schema: bool = False,
    cache_private: bool = True,
    tags: tuple[str, ...] = (),
    docs: str | None = None,
) -> Callable[[Callable[P, R]], AddressableDescriptor[P, R]]: ...


def addressable(
    factory: Callable[P, R] | None = None,
    /,
    *,
    name: str | None = None,
    distribution: str = "hedron-core",
    methods: tuple[str, ...] = ("GET",),
    include_in_schema: bool = False,
    cache_private: bool = True,
    tags: tuple[str, ...] = (),
    docs: str | None = None,
) -> AddressableDescriptor[P, R] | Callable[[Callable[P, R]], AddressableDescriptor[P, R]]:
    """Declare a reusable addressable factory without exposing an HTTP route."""

    def decorate(fn: Callable[P, R]) -> AddressableDescriptor[P, R]:
        logical_name = name or fn.__name__
        module = fn.__module__
        logical_id = component_type_id(distribution, module, logical_name)
        descriptor = AddressableDescriptor(
            factory=fn,
            logical_id=logical_id,
            name=logical_name,
            module=module,
            distribution=distribution,
            methods=tuple(m.upper() for m in methods),
            include_in_schema=include_in_schema,
            cache_private=cache_private,
            tags=tags,
            docs=docs or inspect.getdoc(fn),
        )
        register_addressable(
            logical_id=logical_id,
            name=logical_name,
            module=module,
            distribution=distribution,
            methods=descriptor.methods,
            include_in_schema=include_in_schema,
            cache_private=cache_private,
            tags=tags,
            docs=descriptor.docs,
            factory=fn,
        )
        return descriptor

    if factory is not None:
        return decorate(factory)
    return decorate
