"""Namespaced URL helpers for explicitly exposed Hedron components/actions."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Sequence
from typing import cast

from django.http import HttpRequest, HttpResponseBase
from django.urls import URLPattern, URLResolver, path

from hedron_core.addressable import AddressableDescriptor
from hedron_django.routing import hedron_view

__all__ = ["component_path", "hedron_paths", "include_component_path"]


def component_path(
    route: str,
    view: Callable[..., object],
    *,
    name: str,
) -> URLPattern | URLResolver:
    """Wrap ``view`` with :func:`hedron_view` and return a named ``path``."""
    wrapped = cast(Callable[..., HttpResponseBase], hedron_view(view))
    return path(route, wrapped, name=name)


def include_component_path(
    descriptor: AddressableDescriptor[..., object],
    *,
    route: str,
    name: str | None = None,
) -> URLPattern | URLResolver:
    """Expose an ``@addressable`` factory under Django URL configuration."""

    ep = name or f"hedron_{descriptor.logical_id.replace(':', '_').replace('.', '_')}"

    def view(request: HttpRequest, **kwargs: object) -> object:
        factory = descriptor.factory
        try:
            signature = inspect.signature(factory)
        except (TypeError, ValueError):
            return factory(**kwargs)
        if "request" in signature.parameters:
            return factory(request=request, **kwargs)
        return factory(**kwargs)

    wrapped = cast(Callable[..., HttpResponseBase], hedron_view(view))
    return path(route, wrapped, name=ep)


def hedron_paths(patterns: Sequence[URLPattern | URLResolver]) -> list[URLPattern | URLResolver]:
    """Identity helper documenting a reusable include()-able pattern list."""
    return list(patterns)
