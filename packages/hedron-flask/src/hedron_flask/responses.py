"""Build Flask responses from Hedron components and InteractionResult values."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from flask import Response
from flask import request as flask_request

from hedron_core.builtins.document import Page
from hedron_core.component import Component, NodeLike
from hedron_core.interaction import (
    FragmentRegionError,
    InteractionResult,
    authorize_htmx_target,
    materialize_interaction_nodes,
    merge_interaction_headers,
)
from hedron_core.rendering import RenderContext, RenderMode, RenderResult, render
from hedron_flask.htmx import render_mode_for_request

__all__ = [
    "component_response",
    "interaction_response",
]


def _header_value(headers: Mapping[str, str] | Any, name: str) -> str | None:
    """Read an HTTP header with case-insensitive fallback for plain dicts."""
    getter = getattr(headers, "get", None)
    if callable(getter):
        value = getter(name)
        if value is not None:
            return str(value)
    if isinstance(headers, Mapping):
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
    headers: Mapping[str, str] | None = None,
    context: RenderContext | None = None,
    mode: RenderMode | None = None,
) -> RenderResult:
    if isinstance(value, RenderResult):
        return value
    hdrs = dict(headers) if headers is not None else dict(flask_request.headers)
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
        headers.setdefault("Cache-Control", "private, no-store")


def component_response(
    value: NodeLike | Component[Any] | RenderResult,
    *,
    status_code: int = 200,
    context: RenderContext | None = None,
    mode: RenderMode | None = None,
    extra_headers: Mapping[str, str] | None = None,
    headers_map: Mapping[str, str] | None = None,
    authenticated: bool = False,
) -> Response:
    result = _render_body(value, headers=headers_map, context=context, mode=mode)
    headers = dict(result.headers)
    _merge_vary(headers)
    _apply_auth_cache_headers(headers, authenticated=authenticated)
    if extra_headers:
        headers.update(extra_headers)
    return Response(result.html, status=status_code, mimetype="text/html", headers=headers)


def interaction_response(
    result: InteractionResult,
    *,
    context: RenderContext | None = None,
    mode: RenderMode | None = None,
    extra_headers: Mapping[str, str] | None = None,
    headers_map: Mapping[str, str] | None = None,
    authenticated: bool = False,
) -> Response:
    hdrs = headers_map if headers_map is not None else flask_request.headers
    is_htmx = (_header_value(hdrs, "HX-Request") or "").lower() == "true"
    target = result.region_id or _header_value(hdrs, "HX-Target")
    try:
        authorize_htmx_target(result.policy, target, is_htmx=is_htmx)
        node = materialize_interaction_nodes(result)
    except (FragmentRegionError, ValueError) as exc:
        return Response(str(exc), status=403, mimetype="text/plain")
    headers = merge_interaction_headers(result, extra_headers)
    _apply_auth_cache_headers(headers, authenticated=authenticated)
    body = ""
    if node is not None:
        rendered = _render_body(
            node,
            headers=headers_map,
            context=context,
            mode=mode or RenderMode.FRAGMENT,
        )
        body = rendered.html
    return Response(
        body,
        status=result.status_code,
        mimetype="text/html",
        headers=headers,
    )
