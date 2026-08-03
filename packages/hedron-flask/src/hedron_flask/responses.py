"""Build Flask responses from Hedron components and InteractionResult values."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from flask import Response
from flask import request as flask_request

from hedron_core.builtins.document import Page
from hedron_core.component import Component, NodeLike
from hedron_core.interaction import InteractionResult, interaction_headers
from hedron_core.rendering import RenderContext, RenderMode, RenderResult, render
from hedron_flask.htmx import render_mode_for_request

__all__ = [
    "component_response",
    "interaction_response",
]


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
    headers: Mapping[str, str] | None = None,
    context: RenderContext | None = None,
    mode: RenderMode | None = None,
) -> RenderResult:
    if isinstance(value, RenderResult):
        return value
    hdrs = dict(headers or flask_request.headers)
    selected_mode = render_mode_for_request(hdrs, force=mode)
    render_context = context or RenderContext.standalone()
    to_render: NodeLike | Component[Any] = value
    if selected_mode is RenderMode.FRAGMENT:
        to_render = _fragment_value(value)
    return render(to_render, context=render_context, mode=selected_mode)


def component_response(
    value: NodeLike | Component[Any] | RenderResult,
    *,
    status_code: int = 200,
    context: RenderContext | None = None,
    mode: RenderMode | None = None,
    extra_headers: Mapping[str, str] | None = None,
) -> Response:
    result = _render_body(value, context=context, mode=mode)
    headers = dict(result.headers)
    if extra_headers:
        headers.update(extra_headers)
    return Response(result.html, status=status_code, mimetype="text/html", headers=headers)


def interaction_response(
    result: InteractionResult,
    *,
    context: RenderContext | None = None,
    mode: RenderMode | None = None,
) -> Response:
    headers = interaction_headers(result)
    body = ""
    if result.content is not None:
        rendered = _render_body(result.content, context=context, mode=mode)
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
    return Response(
        body,
        status=result.status_code,
        mimetype="text/html",
        headers=headers,
    )
