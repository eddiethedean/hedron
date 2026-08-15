"""Route registry catalog."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Literal

RouteKind = Literal["page", "component", "action"]


@dataclass(frozen=True, slots=True)
class RouteMeta:
    """Adapter-populated page/action/component route metadata."""

    kind: RouteKind
    logical_id: str
    name: str
    path: str
    methods: tuple[str, ...]
    operation_id: str
    include_in_schema: bool
    module: str
    tags: tuple[str, ...] = ()
    docs: str | None = None
    endpoint: Callable[..., object] | None = None
    htmx_inference: Mapping[str, str] = field(default_factory=dict)


def register_route(
    *,
    kind: RouteKind,
    logical_id: str,
    name: str,
    path: str,
    methods: tuple[str, ...],
    operation_id: str,
    include_in_schema: bool,
    module: str,
    tags: tuple[str, ...] = (),
    docs: str | None = None,
    endpoint: Callable[..., object] | None = None,
    htmx_inference: Mapping[str, str] | None = None,
) -> None:
    from hedron_core.registry.builder import active_builder

    active_builder().register_route(
        RouteMeta(
            kind=kind,
            logical_id=logical_id,
            name=name,
            path=path,
            methods=methods,
            operation_id=operation_id,
            include_in_schema=include_in_schema,
            module=module,
            tags=tags,
            docs=docs,
            endpoint=endpoint,
            htmx_inference=dict(htmx_inference or {}),
        )
    )
