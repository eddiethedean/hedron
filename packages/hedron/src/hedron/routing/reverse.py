"""URL reverse and component references."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal, cast

from hedron_core.registry import get_registry
from hedron_core.typing_aliases import HtmlAttrValue, JsonValue

__all__ = ["ComponentRef", "resolve_route_path"]


@dataclass(frozen=True, slots=True)
class ComponentRef:
    """Registry-backed reference for HTMX controls."""

    logical_id: str
    path: str
    method: str = "GET"
    target: str | None = None
    swap: str = "innerHTML"
    params: Mapping[str, Any] = field(default_factory=dict[str, Any])
    inference: Mapping[str, JsonValue] = field(default_factory=dict[str, JsonValue])

    def htmx_attributes(
        self,
        *,
        target: str | None = None,
        swap: str | None = None,
        trigger: str | None = None,
    ) -> dict[str, HtmlAttrValue]:
        """Return validated generic HTMX attributes for this route reference."""
        from hedron_core.htmx.attrs import HtmxAttrs

        method = self.method.upper()
        url = self.path
        if self.params:
            from urllib.parse import urlencode

            query = urlencode({k: str(v) for k, v in self.params.items()})
            url = f"{url}?{query}" if "?" not in url else f"{url}&{query}"
        return HtmxAttrs(
            method=cast(Literal["get", "post", "put", "patch", "delete"], method.lower()),
            url=url,
            target=target if target is not None else self.target,
            swap=swap if swap is not None else self.swap,
            trigger=trigger,
        ).as_html_attrs()

    def hx_attrs(self) -> dict[str, str]:
        """Compatibility wrapper returning string-valued HTMX attributes."""
        return {name: str(value) for name, value in self.htmx_attributes().items()}


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
