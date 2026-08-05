"""Namespaced URL helpers for explicitly exposed Hedron components/actions."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from django.urls import URLPattern, URLResolver, path

from hedron_core.addressable import AddressableDescriptor
from hedron_django.routing import hedron_view

__all__ = ["component_path", "hedron_paths", "include_component_path"]


def component_path(
    route: str,
    view: Callable[..., Any],
    *,
    name: str,
) -> URLPattern | URLResolver:
    """Wrap ``view`` with :func:`hedron_view` and return a named ``path``."""
    return path(route, hedron_view(view), name=name)


def include_component_path(
    descriptor: AddressableDescriptor[..., Any],
    *,
    route: str,
    name: str | None = None,
) -> URLPattern | URLResolver:
    """Expose an ``@addressable`` factory under Django URL configuration."""

    ep = name or f"hedron_{descriptor.logical_id.replace(':', '_').replace('.', '_')}"

    def view(request: Any, **kwargs: Any) -> Any:
        del request
        return descriptor.factory(**kwargs)

    return path(route, hedron_view(view), name=ep)


def hedron_paths(patterns: Sequence[URLPattern | URLResolver]) -> list[URLPattern | URLResolver]:
    """Identity helper documenting a reusable include()-able pattern list."""
    return list(patterns)
