"""Django routing helpers with portable URL reversal."""

from __future__ import annotations

import inspect
import secrets
from collections.abc import Callable, Sequence
from functools import wraps
from typing import Any, TypeVar, cast, overload

from asgiref.sync import markcoroutinefunction
from django.http import HttpRequest, HttpResponse
from django.urls import reverse

from hedron_core.adapter import UrlReverseRequest
from hedron_core.component import Component, ComponentNode, NodeLike
from hedron_core.interaction import FragmentRegion, InteractionResult
from hedron_core.interaction_067 import Outcome
from hedron_core.mount import prefix_local_path
from hedron_core.rendering import RenderResult
from hedron_django.csrf import DjangoCsrfError, seed_csrf_cookie, validate_csrf
from hedron_django.responses import (
    _outcome_response,  # pyright: ignore[reportPrivateUsage]
    component_response,
    interaction_response,
)

__all__ = [
    "DjangoUrlReverser",
    "HEDRON_APP_ID",
    "action",
    "hedron_view",
    "page",
    "view",
]

F = TypeVar("F", bound=Callable[..., Any])

HEDRON_APP_ID = secrets.token_hex(8)


class DjangoUrlReverser:
    """Reverse named URL patterns via Django ``reverse``."""

    def reverse(self, request: UrlReverseRequest) -> str:
        path = reverse(request.name, args=request.args, kwargs=dict(request.kwargs))
        if request.script_name:
            path = prefix_local_path(path, request.script_name)
        if request.root_path:
            path = prefix_local_path(path, request.root_path)
        return path


def _as_node_like(value: object) -> NodeLike | Component[Any]:
    if isinstance(value, Component):
        return cast(Component[Any], value)
    if isinstance(value, ComponentNode):
        return value
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    # Duck-typed host markers (``__hedron_component__``) are treated as nodes.
    return cast(NodeLike, value)


def _convert(
    value: object,
    request: HttpRequest,
    *,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
    skip_prepare: bool = False,
) -> HttpResponse:
    method = (request.method or "GET").upper()
    if method in {"GET", "HEAD"}:
        seed_csrf_cookie(request)
    else:
        try:
            validate_csrf(request)
        except DjangoCsrfError as exc:
            return HttpResponse(str(exc).encode("utf-8"), status=403, content_type="text/plain")
    authenticated = bool(getattr(getattr(request, "user", None), "is_authenticated", False))
    from hedron_core.diagnostics import HedronError
    from hedron_core.updates import compile_to_interaction

    try:
        value = compile_to_interaction(value, expected_app_id=HEDRON_APP_ID)
    except HedronError as exc:
        code = getattr(exc.diagnostic, "code", "")
        status = 403 if str(code).startswith("HED-UPDATE-0003") else 400
        return HttpResponse(str(exc).encode("utf-8"), status=status, content_type="text/plain")
    if isinstance(value, Outcome):
        return _outcome_response(
            value,
            request=request,
            authenticated=authenticated,
            fragment_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
            app_id=HEDRON_APP_ID,
        )
    if isinstance(value, InteractionResult):
        return interaction_response(
            value,
            request=request,
            authenticated=authenticated,
            fragment_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
            skip_prepare=skip_prepare,
        )
    if isinstance(value, RenderResult):
        return component_response(
            value,
            request=request,
            authenticated=authenticated,
            fragment_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
            skip_prepare=skip_prepare,
        )
    if isinstance(value, (Component, str, ComponentNode)) or hasattr(value, "__hedron_component__"):
        return component_response(
            _as_node_like(cast(object, value)),
            request=request,
            authenticated=authenticated,
            fragment_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
            skip_prepare=skip_prepare,
        )
    if isinstance(value, HttpResponse):
        return value
    raise TypeError(f"Unsupported Hedron view return type: {type(value)!r}")


def _csrf_gate(request: HttpRequest) -> HttpResponse | None:
    """Reject unsafe methods before the view runs (Flask/FastAPI parity, #392)."""
    method = (request.method or "GET").upper()
    if method in {"GET", "HEAD"}:
        seed_csrf_cookie(request)
        return None
    try:
        validate_csrf(request)
    except DjangoCsrfError as exc:
        return HttpResponse(str(exc).encode("utf-8"), status=403, content_type="text/plain")
    return None


async def _convert_async(
    value: object,
    request: HttpRequest,
    *,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
) -> HttpResponse:
    """ASGI path: await prepare_tree before converting to HttpResponse."""
    from hedron_core.diagnostics import HedronError
    from hedron_core.prepare import prepare_tree
    from hedron_core.updates import compile_to_interaction

    try:
        value = compile_to_interaction(value, expected_app_id=HEDRON_APP_ID)
    except HedronError as exc:
        code = getattr(exc.diagnostic, "code", "")
        status = 403 if str(code).startswith("HED-UPDATE-0003") else 400
        return HttpResponse(str(exc).encode("utf-8"), status=status, content_type="text/plain")
    if isinstance(value, InteractionResult):
        if value.content is not None:
            await prepare_tree(value.content)
        for update in value.oob:
            await prepare_tree(update.content)
    elif (
        isinstance(value, (Component, str, ComponentNode)) or hasattr(value, "__hedron_component__")
    ) and not isinstance(value, RenderResult):
        await prepare_tree(_as_node_like(cast(object, value)))
    return _convert(
        cast(object, value),
        request,
        fragment_regions=fragment_regions,
        allow_undeclared_targets=allow_undeclared_targets,
        skip_prepare=True,
    )


@overload
def hedron_view(
    view: F,
    *,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
) -> F: ...


@overload
def hedron_view(
    view: None = None,
    *,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
) -> Callable[[F], F]: ...


def hedron_view(
    view: F | None = None,
    *,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
) -> F | Callable[[F], F]:
    """Wrap a view so components and InteractionResult values become HttpResponse."""

    def decorator(fn: F) -> F:
        if inspect.iscoroutinefunction(fn):

            @wraps(fn)
            async def async_wrapped(
                request: HttpRequest, *args: object, **kwargs: object
            ) -> HttpResponse:
                denied = _csrf_gate(request)
                if denied is not None:
                    return denied
                value = await fn(request, *args, **kwargs)
                return await _convert_async(
                    value,
                    request,
                    fragment_regions=fragment_regions,
                    allow_undeclared_targets=allow_undeclared_targets,
                )

            markcoroutinefunction(async_wrapped)
            return cast(F, async_wrapped)

        @wraps(fn)
        def wrapped(request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
            denied = _csrf_gate(request)
            if denied is not None:
                return denied
            value = fn(request, *args, **kwargs)
            return _convert(
                value,
                request,
                fragment_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
            )

        return cast(F, wrapped)

    if view is not None:
        return decorator(view)
    return decorator


# Canonical adapter spellings.  Django's URL resolver owns route registration,
# so page/view share the response-lowering wrapper and remain ordinary
# function decorators.  ``hedron_view`` stays exported as the 0.67 spelling.
@overload
def view(
    handler: F,
    *,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
) -> F: ...


@overload
def view(
    handler: None = None,
    *,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
) -> Callable[[F], F]: ...


def view(
    handler: F | None = None,
    *,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
) -> F | Callable[[F], F]:
    return hedron_view(
        handler,
        fragment_regions=fragment_regions,
        allow_undeclared_targets=allow_undeclared_targets,
    )


@overload
def page(
    handler: F,
    *,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
) -> F: ...


@overload
def page(
    handler: None = None,
    *,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
) -> Callable[[F], F]: ...


def page(
    handler: F | None = None,
    *,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
) -> F | Callable[[F], F]:
    return hedron_view(
        handler,
        fragment_regions=fragment_regions,
        allow_undeclared_targets=allow_undeclared_targets,
    )


@overload
def action(
    handler: F,
    *,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
) -> F: ...


@overload
def action(
    handler: None = None,
    *,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
) -> Callable[[F], F]: ...


def action(
    handler: F | None = None,
    *,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
) -> F | Callable[[F], F]:
    """Wrap a mutation handler with canonical response and CSRF lowering."""

    def decorate(fn: F) -> F:
        wrapped = hedron_view(
            fn,
            fragment_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
        )

        if inspect.iscoroutinefunction(fn):

            @wraps(wrapped)
            async def async_action(request: HttpRequest, *args: object, **kwargs: object) -> Any:
                if (request.method or "").upper() not in {"POST", "PUT", "PATCH", "DELETE"}:
                    return HttpResponse(status=405)
                return await wrapped(request, *args, **kwargs)

            markcoroutinefunction(async_action)
            return cast(F, async_action)

        @wraps(wrapped)
        def sync_action(request: HttpRequest, *args: object, **kwargs: object) -> Any:
            if (request.method or "").upper() not in {"POST", "PUT", "PATCH", "DELETE"}:
                return HttpResponse(status=405)
            return wrapped(request, *args, **kwargs)

        return cast(F, sync_action)

    return decorate(handler) if handler is not None else decorate
