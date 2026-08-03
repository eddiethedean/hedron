"""Build Django HttpResponse values from Hedron components and InteractionResult."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from django.http import HttpRequest, HttpResponse

from hedron_core.builtins.document import Page
from hedron_core.component import Component, NodeLike
from hedron_core.interaction import InteractionResult, interaction_headers
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
    if extra_headers:
        headers.update(extra_headers)
    return HttpResponse(result.html, status=status_code, content_type="text/html", headers=headers)


def interaction_response(
    result: InteractionResult,
    *,
    request: HttpRequest | None = None,
    context: RenderContext | None = None,
    mode: RenderMode | None = None,
) -> HttpResponse:
    headers = interaction_headers(result)
    body = ""
    if result.content is not None:
        rendered = _render_body(result.content, request=request, context=context, mode=mode)
        body = rendered.html
    if result.oob:
        from hedron_core.rendering import render as core_render

        render_context = context or RenderContext.standalone()
        parts: list[str] = [body]
        for update in result.oob:
            chunk = core_render(update.content, context=render_context, mode=RenderMode.FRAGMENT)
            tag = chunk.html
            if update.element_id and 'id="' not in tag:
                tag = tag.replace(">", f' id="{update.element_id}" hx-swap-oob="{update.swap}">', 1)
            elif update.swap != "true" and "hx-swap-oob" not in tag:
                tag = tag.replace(">", f' hx-swap-oob="{update.swap}">', 1)
            parts.append(tag)
        body = "".join(parts)
    return HttpResponse(body, status=result.status_code, content_type="text/html", headers=headers)
