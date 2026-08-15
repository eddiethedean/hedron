"""Addressable registry catalog."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AddressableMeta:
    logical_id: str
    name: str
    module: str
    distribution: str
    methods: tuple[str, ...]
    include_in_schema: bool
    cache_private: bool
    tags: tuple[str, ...]
    docs: str | None
    factory: Callable[..., object] | None = None
    route: str | None = None


def register_addressable(
    *,
    logical_id: str,
    name: str,
    module: str,
    distribution: str = "hedron-core",
    methods: tuple[str, ...] = ("GET",),
    include_in_schema: bool = False,
    cache_private: bool = True,
    tags: tuple[str, ...] = (),
    docs: str | None = None,
    factory: Callable[..., object] | None = None,
    route: str | None = None,
) -> None:
    from hedron_core.registry.builder import active_builder

    active_builder().register_addressable(
        AddressableMeta(
            logical_id=logical_id,
            name=name,
            module=module,
            distribution=distribution,
            methods=methods,
            include_in_schema=include_in_schema,
            cache_private=cache_private,
            tags=tags,
            docs=docs,
            factory=factory,
            route=route,
        )
    )
