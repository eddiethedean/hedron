"""Django routing helpers with portable URL reversal."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Sequence
from functools import wraps
from typing import Any, TypeVar

from asgiref.sync import markcoroutinefunction
from django.http import HttpRequest, HttpResponse
from django.urls import reverse

from hedron_core.adapter import UrlReverseRequest
from hedron_core.component import Component
from hedron_core.interaction import FragmentRegion, InteractionResult
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


def _convert(
    value: object,
    request: HttpRequest,
    *,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
) -> HttpResponse:
    from hedron_django.csrf import seed_csrf_cookie

    if (request.method or "GET").upper() in {"GET", "HEAD"}:
        seed_csrf_cookie(request)
    authenticated = bool(getattr(getattr(request, "user", None), "is_authenticated", False))
    if isinstance(value, InteractionResult):
        return interaction_response(
            value,
            request=request,
            authenticated=authenticated,
            fragment_regions=fragment_regions,
        )
    if isinstance(value, RenderResult):
        return component_response(
            value,
            request=request,
            authenticated=authenticated,
            fragment_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
        )
    if isinstance(value, (Component, str)) or hasattr(value, "__hedron_component__"):
        return component_response(
            value,  # type: ignore[arg-type]
            request=request,
            authenticated=authenticated,
            fragment_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
        )
    if isinstance(value, HttpResponse):
        return value
    raise TypeError(f"Unsupported Hedron view return type: {type(value)!r}")


async def _convert_async(
    value: object,
    request: HttpRequest,
    *,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
) -> HttpResponse:
    """ASGI path: await prepare_tree before converting to HttpResponse."""
    from hedron_core.prepare import prepare_tree

    if (
        (isinstance(value, (Component, str)) or hasattr(value, "__hedron_component__"))
        and not isinstance(value, RenderResult)
        and not isinstance(value, InteractionResult)
    ):
        await prepare_tree(value)  # type: ignore[arg-type]
    return _convert(
        value,
        request,
        fragment_regions=fragment_regions,
        allow_undeclared_targets=allow_undeclared_targets,
    )


def hedron_view(
    view: F | None = None,
    *,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
) -> Any:
    """Wrap a view so components and InteractionResult values become HttpResponse."""

    def decorator(fn: F) -> F:
        if inspect.iscoroutinefunction(fn):

            @wraps(fn)
            async def async_wrapped(
                request: HttpRequest, *args: object, **kwargs: object
            ) -> HttpResponse:
                value = await fn(request, *args, **kwargs)
                return await _convert_async(
                    value,
                    request,
                    fragment_regions=fragment_regions,
                    allow_undeclared_targets=allow_undeclared_targets,
                )

            markcoroutinefunction(async_wrapped)
            return async_wrapped  # type: ignore[return-value]

        @wraps(fn)
        def wrapped(request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
            value = fn(request, *args, **kwargs)
            return _convert(
                value,
                request,
                fragment_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
            )

        return wrapped  # type: ignore[return-value]

    if view is not None:
        return decorator(view)
    return decorator
