"""Build Django HttpResponse values from Hedron components and InteractionResult."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from django.http import HttpRequest, HttpResponse

from hedron_core.audit import SecurityAuditEventType, emit_security_audit
from hedron_core.builtins.document import Page
from hedron_core.component import Component, NodeLike
from hedron_core.interaction import (
    FragmentRegion,
    FragmentRegionError,
    InteractionPolicy,
    InteractionResult,
    authorize_htmx_target,
    materialize_interaction_nodes,
    merge_interaction_headers,
    merge_route_regions,
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


def _normalize_regions(
    fragment_regions: Sequence[FragmentRegion | str] | None,
) -> tuple[FragmentRegion, ...]:
    if not fragment_regions:
        return ()
    out: list[FragmentRegion] = []
    for region in fragment_regions:
        if isinstance(region, FragmentRegion):
            out.append(region)
        else:
            name = str(region).lstrip("#")
            out.append(FragmentRegion(id=name, selector=f"#{name}"))
    return tuple(out)


def _authorize_component_htmx(
    *,
    request: HttpRequest | None,
    headers_map: Mapping[str, str],
    fragment_regions: tuple[FragmentRegion, ...],
    allow_undeclared_targets: bool = False,
) -> None:
    is_htmx = (_header_value(headers_map, "HX-Request") or "").lower() == "true"
    if not is_htmx:
        return
    target = _header_value(headers_map, "HX-Target")
    try:
        authorize_htmx_target(
            InteractionPolicy(
                declared_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
            ),
            target,
            is_htmx=True,
        )
    except FragmentRegionError as exc:
        path = getattr(request, "path", "") if request is not None else ""
        emit_security_audit(
            SecurityAuditEventType.HTMX_TARGET_REJECTED,
            str(exc),
            attributes={"path": path, "target": target},
        )
        raise


def _maybe_prepare(value: NodeLike | Component[Any] | RenderResult) -> None:
    """Best-effort prepare_tree before sync render (WSGI / no running loop)."""
    if isinstance(value, RenderResult):
        return
    from hedron_core.async_bridge import run_prepare
    from hedron_core.prepare import prepare_tree

    run_prepare(lambda: prepare_tree(value))


def _default_render_context(request: HttpRequest | None) -> RenderContext:
    """Populate Django CSRF token under ``csrfmiddlewaretoken`` for ``CsrfField``."""
    if request is None:
        return RenderContext.standalone()
    csrf_token: str | None = None
    try:
        from django.middleware.csrf import get_token

        token = get_token(request)
        if isinstance(token, str) and token:
            csrf_token = token
    except Exception:
        csrf_token = None
    return RenderContext.standalone(
        csrf_token=csrf_token,
        csrf_form_field="csrfmiddlewaretoken",
    )


def _render_body(
    value: NodeLike | Component[Any] | RenderResult,
    *,
    request: HttpRequest | None = None,
    context: RenderContext | None = None,
    mode: RenderMode | None = None,
) -> RenderResult:
    if isinstance(value, RenderResult):
        return value
    _maybe_prepare(value)
    hdrs = _headers_mapping(request)
    selected_mode = render_mode_for_request(hdrs, force=mode)
    render_context = context or _default_render_context(request)
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
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
) -> HttpResponse:
    hdrs = _headers_mapping(request)
    try:
        _authorize_component_htmx(
            request=request,
            headers_map=hdrs,
            fragment_regions=_normalize_regions(fragment_regions),
            allow_undeclared_targets=allow_undeclared_targets,
        )
    except FragmentRegionError as exc:
        return HttpResponse(
            str(exc).encode("utf-8"),
            status=403,
            content_type="text/plain; charset=utf-8",
        )
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
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
) -> HttpResponse:
    hdrs = _headers_mapping(request)
    regions = _normalize_regions(fragment_regions)
    if regions:
        result = merge_route_regions(result, regions)
    is_htmx = (_header_value(hdrs, "HX-Request") or "").lower() == "true"
    client_target = _header_value(hdrs, "HX-Target")
    try:
        target = select_htmx_auth_target(client_target=client_target, region_id=result.region_id)
        authorize_htmx_target(result.policy, target, is_htmx=is_htmx)
        node = materialize_interaction_nodes(result)
    except (FragmentRegionError, ValueError) as exc:
        path = getattr(request, "path", "") if request is not None else ""
        emit_security_audit(
            SecurityAuditEventType.HTMX_TARGET_REJECTED,
            str(exc),
            attributes={"path": path, "target": client_target},
        )
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
