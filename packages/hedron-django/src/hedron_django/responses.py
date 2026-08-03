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
    interaction_headers,
    materialize_interaction_nodes,
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
    return {k: v for k, v in request.headers.items()}


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


def component_response(
    value: NodeLike | Component[Any] | RenderResult,
    *,
    request: HttpRequest | None = None,
    status_code: int = 200,
    context: RenderContext | None = None,
    mode: RenderMode | None = None,
    extra_headers: Mapping[str, str] | None = None,
) -> HttpResponse:
    result = _render_body(value, request=request, context=context, mode=mode)
    headers = dict(result.headers)
    _merge_vary(headers)
    if extra_headers:
        headers.update(extra_headers)
    return HttpResponse(result.html, status=status_code, content_type="text/html", headers=headers)


def interaction_response(
    result: InteractionResult,
    *,
    request: HttpRequest | None = None,
    context: RenderContext | None = None,
    mode: RenderMode | None = None,
    extra_headers: Mapping[str, str] | None = None,
) -> HttpResponse:
    try:
        node = materialize_interaction_nodes(result)
    except (FragmentRegionError, ValueError) as exc:
        return HttpResponse(str(exc), status=403, content_type="text/plain")
    headers = interaction_headers(result)
    if extra_headers:
        headers.update(dict(extra_headers))
    body = ""
    if node is not None:
        rendered = _render_body(
            node,
            request=request,
            context=context,
            mode=mode or RenderMode.FRAGMENT,
        )
        body = rendered.html
    return HttpResponse(body, status=result.status_code, content_type="text/html", headers=headers)
