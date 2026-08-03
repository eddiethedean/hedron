"""URL reverse and component references."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from hedron_core.registry import get_registry

__all__ = ["ComponentRef", "resolve_route_path"]


@dataclass(frozen=True, slots=True)
class ComponentRef:
    """Registry-backed reference for HTMX controls."""

    logical_id: str
    path: str
    method: str = "GET"
    target: str | None = None
    swap: str = "innerHTML"
    params: Mapping[str, Any] = field(default_factory=dict)
    inference: Mapping[str, str] = field(default_factory=dict)

    def hx_attrs(self) -> dict[str, str]:
        attrs: dict[str, str] = {}
        method = self.method.upper()
        url = self.path
        if self.params:
            from urllib.parse import urlencode

            query = urlencode({k: str(v) for k, v in self.params.items()})
            url = f"{url}?{query}" if "?" not in url else f"{url}&{query}"
        if method == "GET":
            attrs["hx-get"] = url
        elif method == "POST":
            attrs["hx-post"] = url
        elif method == "PUT":
            attrs["hx-put"] = url
        elif method == "PATCH":
            attrs["hx-patch"] = url
        elif method == "DELETE":
            attrs["hx-delete"] = url
        else:
            attrs["hx-get"] = url
        if self.target:
            attrs["hx-target"] = self.target
        if self.swap:
            attrs["hx-swap"] = self.swap
        return attrs


def resolve_route_path(logical_id: str, *, kind: str | None = None) -> ComponentRef | None:
    registry = get_registry()
    for route in registry.routes():
        if route.logical_id != logical_id:
            continue
        if kind is not None and route.kind != kind:
            continue
        method = route.methods[0] if route.methods else "GET"
        return ComponentRef(
            logical_id=logical_id,
            path=route.path,
            method=method,
            inference=dict(route.htmx_inference),
        )
    addressable = registry.get_addressable(logical_id)
    if addressable and addressable.route:
        return ComponentRef(
            logical_id=logical_id,
            path=addressable.route,
            method=addressable.methods[0] if addressable.methods else "GET",
        )
    return None
