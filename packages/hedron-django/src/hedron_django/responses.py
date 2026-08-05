"""Build Django HttpResponse values from Hedron components and InteractionResult."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from django.http import HttpRequest, HttpResponse

from hedron_core.builtins.document import Page
from hedron_core.component import Component, NodeLike
from hedron_core.interaction import (
    FragmentRegionError,
    InteractionResult,
    authorize_htmx_target,
    materialize_interaction_nodes,
    merge_interaction_headers,
    select_htmx_auth_target,
)
from hedron_core.rendering import RenderContext, RenderMode, RenderResult, render
from hedron_django.htmx import render_mode_for_request

__all__ = [
    "component_response",
    "interaction_response",
]


def _headers_mapping(request: HttpRequest | None) -> dict[str, str]:
    if request is None:
        return {}
    headers = getattr(request, "headers", None)
    items = getattr(headers, "items", None)
    if not callable(items):
        return {}
    raw_items = items()
    if not isinstance(raw_items, (list, tuple)):
        try:
            raw_items = list(raw_items)  # type: ignore[arg-type]
        except TypeError:
            return {}
    return {str(k): str(v) for k, v in raw_items}


def _header_value(headers: Mapping[str, str], name: str) -> str | None:
    """Read an HTTP header with case-insensitive fallback for plain dicts."""
    value = headers.get(name)
    if value is not None:
        return str(value)
    lower = name.lower()
    for key, val in headers.items():
        if str(key).lower() == lower:
            return str(val)
    return None


def _fragment_value(value: NodeLike | Component[Any]) -> NodeLike | Component[Any]:
    if isinstance(value, Page):
        children = list(value._children)
        if len(children) == 1:
            return children[0]  # type: ignore[no-any-return]
        return children  # type: ignore[return-value]
    return value


def _render_body(
    value: NodeLike | Component[Any] | RenderResult,
    *,
    request: HttpRequest | None = None,
    context: RenderContext | None = None,
    mode: RenderMode | None = None,
) -> RenderResult:
    if isinstance(value, RenderResult):
        return value
    hdrs = _headers_mapping(request)
    selected_mode = render_mode_for_request(hdrs, force=mode)
    render_context = context or RenderContext.standalone()
    to_render: NodeLike | Component[Any] = value
    if selected_mode is RenderMode.FRAGMENT:
        to_render = _fragment_value(value)
    return render(to_render, context=render_context, mode=selected_mode)


def _merge_vary(headers: dict[str, str]) -> None:
    existing = {p.strip() for p in headers.get("Vary", "").split(",") if p.strip()}
    existing.update({"HX-Request", "HX-History-Restore-Request"})
    headers["Vary"] = ", ".join(sorted(existing))


def _apply_auth_cache_headers(headers: dict[str, str], *, authenticated: bool) -> None:
    if authenticated:
        # Force private caching; never leave a caller-supplied public/shared directive.
        headers["Cache-Control"] = "private, no-store"


def component_response(
    value: NodeLike | Component[Any] | RenderResult,
    *,
    request: HttpRequest | None = None,
    status_code: int = 200,
    context: RenderContext | None = None,
    mode: RenderMode | None = None,
    extra_headers: Mapping[str, str] | None = None,
    authenticated: bool = False,
) -> HttpResponse:
    result = _render_body(value, request=request, context=context, mode=mode)
    headers = dict(result.headers)
    _merge_vary(headers)
    _apply_auth_cache_headers(headers, authenticated=authenticated)
    if extra_headers:
        headers.update(extra_headers)
        _apply_auth_cache_headers(headers, authenticated=authenticated)
    return HttpResponse(
        result.html.encode("utf-8"),
        status=status_code,
        content_type="text/html; charset=utf-8",
        headers=headers,
    )


def interaction_response(
    result: InteractionResult,
    *,
    request: HttpRequest | None = None,
    context: RenderContext | None = None,
    mode: RenderMode | None = None,
    extra_headers: Mapping[str, str] | None = None,
    authenticated: bool = False,
) -> HttpResponse:
    hdrs = _headers_mapping(request)
    is_htmx = (_header_value(hdrs, "HX-Request") or "").lower() == "true"
    client_target = _header_value(hdrs, "HX-Target")
    try:
        target = select_htmx_auth_target(client_target=client_target, region_id=result.region_id)
        authorize_htmx_target(result.policy, target, is_htmx=is_htmx)
        node = materialize_interaction_nodes(result)
    except (FragmentRegionError, ValueError) as exc:
        return HttpResponse(
            str(exc).encode("utf-8"),
            status=403,
            content_type="text/plain; charset=utf-8",
        )
    headers = merge_interaction_headers(result, extra_headers)
    _apply_auth_cache_headers(headers, authenticated=authenticated)
    body = ""
    if node is not None:
        rendered = _render_body(
            node,
            request=request,
            context=context,
            mode=mode or RenderMode.FRAGMENT,
        )
        body = rendered.html
    return HttpResponse(
        body.encode("utf-8"),
        status=result.status_code,
        content_type="text/html; charset=utf-8",
        headers=headers,
    )
