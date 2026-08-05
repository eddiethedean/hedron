"""Django routing helpers with portable URL reversal."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from asgiref.sync import markcoroutinefunction
from django.http import HttpRequest, HttpResponse
from django.urls import reverse

from hedron_core.adapter import UrlReverseRequest
from hedron_core.component import Component
from hedron_core.interaction import InteractionResult
from hedron_core.rendering import RenderResult
from hedron_django.responses import component_response, interaction_response

__all__ = [
    "DjangoUrlReverser",
    "hedron_view",
]

F = TypeVar("F", bound=Callable[..., Any])


class DjangoUrlReverser:
    """Reverse named URL patterns via Django ``reverse``."""

    def reverse(self, request: UrlReverseRequest) -> str:
        path = reverse(request.name, args=request.args, kwargs=dict(request.kwargs))
        if request.script_name:
            prefix = request.script_name.rstrip("/")
            if not path.startswith(prefix):
                path = f"{prefix}{path}"
        if request.root_path:
            root = request.root_path.rstrip("/")
            if not path.startswith(root):
                path = f"{root}{path}"
        return path


def _convert(value: object, request: HttpRequest) -> HttpResponse:
    from hedron_django.csrf import seed_csrf_cookie

    if (request.method or "GET").upper() in {"GET", "HEAD"}:
        seed_csrf_cookie(request)
    authenticated = bool(getattr(getattr(request, "user", None), "is_authenticated", False))
    if isinstance(value, InteractionResult):
        return interaction_response(value, request=request, authenticated=authenticated)
    if isinstance(value, RenderResult):
        return component_response(value, request=request, authenticated=authenticated)
    if isinstance(value, (Component, str)) or hasattr(value, "__hedron_component__"):
        return component_response(value, request=request, authenticated=authenticated)  # type: ignore[arg-type]
    if isinstance(value, HttpResponse):
        return value
    raise TypeError(f"Unsupported Hedron view return type: {type(value)!r}")


def hedron_view(view: F) -> F:
    """Wrap a view so components and InteractionResult values become HttpResponse."""

    if inspect.iscoroutinefunction(view):

        @wraps(view)
        async def async_wrapped(
            request: HttpRequest, *args: object, **kwargs: object
        ) -> HttpResponse:
            value = await view(request, *args, **kwargs)
            return _convert(value, request)

        markcoroutinefunction(async_wrapped)
        return async_wrapped  # type: ignore[return-value]

    @wraps(view)
    def wrapped(request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        value = view(request, *args, **kwargs)
        return _convert(value, request)

    return wrapped  # type: ignore[return-value]
