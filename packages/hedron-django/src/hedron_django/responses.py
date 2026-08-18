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
    validated_extra_headers,
)
from hedron_core.mount import normalize_mount_path, prefix_local_path
from hedron_core.page_assets import inject_page_assets
from hedron_core.rendering import RenderContext, RenderMode, RenderResult, render
from hedron_core.security_policy import SecurityPolicy
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
            name = str(region).removeprefix("#")
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
    history_restore = (
        _header_value(headers_map, "HX-History-Restore-Request") or ""
    ).lower() == "true"
    try:
        authorize_htmx_target(
            InteractionPolicy(
                declared_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
            ),
            target,
            is_htmx=True,
            history_restore=history_restore,
        )
    except FragmentRegionError as exc:
        path = getattr(request, "path", "") if request is not None else ""
        emit_security_audit(
            SecurityAuditEventType.HTMX_TARGET_REJECTED,
            str(exc),
            attributes={"path": path, "target": target},
        )
        raise


def _maybe_prepare(
    value: NodeLike | Component[Any] | RenderResult,
    *,
    skip_prepare: bool = False,
) -> None:
    """Run prepare_tree before sync render (WSGI / no running loop).

    When an event loop is already running, refuse unless ``skip_prepare`` is set
    (ASGI callers must await ``prepare_tree`` then pass ``skip_prepare=True``).
    """
    if skip_prepare or isinstance(value, RenderResult):
        return
    from hedron_core.async_bridge import run_prepare, running_loop
    from hedron_core.prepare import prepare_tree

    if running_loop():
        raise RuntimeError(
            "component prepare cannot run while an event loop is already running; "
            "await prepare_tree(...) then pass skip_prepare=True, or use respond_async()."
        )
    run_prepare(lambda: prepare_tree(value))


def _default_render_context(request: HttpRequest | None) -> RenderContext:
    """Populate Django CSRF token under ``csrfmiddlewaretoken`` for ``CsrfField``."""
    if request is None:
        return RenderContext.standalone()
    csrf_token: str | None = None
    try:
        from django.core.exceptions import ImproperlyConfigured
    except ImportError:
        return RenderContext.standalone(csrf_form_field="csrfmiddlewaretoken")
    try:
        from django.middleware.csrf import get_token

        token = get_token(request)
        if isinstance(token, str) and token:
            csrf_token = token
    except ImproperlyConfigured:
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
    skip_prepare: bool = False,
) -> RenderResult:
    from hedron_core.htmx_eval import reset_htmx_eval_allowed, set_htmx_eval_allowed

    if isinstance(value, RenderResult):
        return value
    policy = _security_policy_from_settings()
    eval_token = set_htmx_eval_allowed(policy.allow_htmx_eval)
    try:
        _maybe_prepare(value, skip_prepare=skip_prepare)
        hdrs = _headers_mapping(request)
        selected_mode = render_mode_for_request(hdrs, force=mode)
        render_context = context or _default_render_context(request)
        to_render: NodeLike | Component[Any] = value
        if selected_mode is RenderMode.FRAGMENT:
            to_render = _fragment_value(value)
        return render(to_render, context=render_context, mode=selected_mode)
    finally:
        reset_htmx_eval_allowed(eval_token)


def _merge_vary(headers: dict[str, str], *, include_target: bool = False) -> None:
    existing = {p.strip() for p in headers.get("Vary", "").split(",") if p.strip()}
    existing.update({"HX-Request", "HX-History-Restore-Request"})
    if include_target or "HX-Target" in existing:
        existing.add("HX-Target")
    headers["Vary"] = ", ".join(sorted(existing))


def _apply_auth_cache_headers(headers: dict[str, str], *, authenticated: bool) -> None:
    if authenticated:
        # Force private caching; never leave a caller-supplied public/shared directive.
        headers["Cache-Control"] = "private, no-store"
    else:
        existing = headers.get("Cache-Control", "")
        lowered = existing.lower()
        if (
            not existing
            or "public" in lowered
            or "s-maxage" in lowered
            or ("private" not in lowered and "no-store" not in lowered)
        ):
            headers["Cache-Control"] = "private, no-store"


def _security_policy_from_settings() -> SecurityPolicy:
    try:
        from django.conf import settings
        from django.core.exceptions import ImproperlyConfigured
    except ImportError:
        return SecurityPolicy.from_name("standard")
    try:
        name = getattr(settings, "HEDRON_SECURITY_PROFILE", "standard")
        return SecurityPolicy.from_name(str(name))
    except ImproperlyConfigured:
        return SecurityPolicy.from_name("standard")


def _django_static_href(path: str) -> str:
    href = path if path.startswith("/") else f"/{path}"
    script = ""
    try:
        from django.urls import get_script_prefix

        script = get_script_prefix() or ""
    except Exception:  # noqa: BLE001
        script = ""
    mount = normalize_mount_path(str(script).rstrip("/") or "")
    return prefix_local_path(href, mount)


def _render_theme(result: RenderResult) -> str | None:
    theme = result.trace.get("theme") if result.trace is not None else None
    return theme if isinstance(theme, str) else None


def _inject_page_html(
    html_text: str,
    mode: RenderMode,
    *,
    theme: str | None = None,
    plan: object | None = None,
    assets: object | None = None,
) -> str:
    from hedron_core.htmx_extensions import ExtensionPlan

    resolved = plan if isinstance(plan, ExtensionPlan) else None
    return inject_page_assets(
        html_text,
        mode,
        policy=_security_policy_from_settings(),
        static_href=_django_static_href,
        theme=theme,
        plan=resolved,
        assets=assets if isinstance(assets, tuple) else None,
    )


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
    skip_prepare: bool = False,
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
        from hedron_core.htmx.authorize import fragment_region_http_detail

        return HttpResponse(
            fragment_region_http_detail(exc).encode("utf-8"),
            status=403,
            content_type="text/plain; charset=utf-8",
        )
    result = _render_body(
        value, request=request, context=context, mode=mode, skip_prepare=skip_prepare
    )
    headers = dict(result.headers)
    _merge_vary(headers)
    _apply_auth_cache_headers(headers, authenticated=authenticated)
    if extra_headers:
        try:
            headers.update(validated_extra_headers(extra_headers))
        except ValueError as exc:
            return HttpResponse(
                str(exc).encode("utf-8"),
                status=403,
                content_type="text/plain; charset=utf-8",
            )
        _apply_auth_cache_headers(headers, authenticated=authenticated)
    selected_mode = render_mode_for_request(hdrs, force=mode)
    body = _inject_page_html(
        result.html,
        selected_mode,
        theme=_render_theme(result),
        plan=getattr(result, "htmx_plan", None),
        assets=result.assets,
    )
    return HttpResponse(
        body.encode("utf-8"),
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
    allow_undeclared_targets: bool = False,
    skip_prepare: bool = False,
) -> HttpResponse:
    from hedron_core.interaction import apply_allow_undeclared_targets

    hdrs = _headers_mapping(request)
    result = apply_allow_undeclared_targets(result, allow_undeclared_targets)
    regions = _normalize_regions(fragment_regions)
    if regions:
        result = merge_route_regions(result, regions)
    is_htmx = (_header_value(hdrs, "HX-Request") or "").lower() == "true"
    client_target = _header_value(hdrs, "HX-Target")
    history_restore = (_header_value(hdrs, "HX-History-Restore-Request") or "").lower() == "true"
    try:
        if result.status_code == 204 and result.oob:
            raise ValueError("OOB updates are not allowed on 204 InteractionResult responses")
        target = select_htmx_auth_target(client_target=client_target, region_id=result.region_id)
        authorize_htmx_target(
            result.policy,
            target,
            is_htmx=is_htmx,
            history_restore=history_restore,
        )
        node = materialize_interaction_nodes(result)
        headers = merge_interaction_headers(result, extra_headers)
    except (FragmentRegionError, ValueError, TypeError) as exc:
        path = getattr(request, "path", "") if request is not None else ""
        emit_security_audit(
            SecurityAuditEventType.HTMX_TARGET_REJECTED,
            str(exc),
            attributes={"path": path, "target": client_target},
        )
        from hedron_core.htmx.authorize import fragment_region_http_detail

        detail = (
            fragment_region_http_detail(exc) if isinstance(exc, FragmentRegionError) else str(exc)
        )
        return HttpResponse(
            detail.encode("utf-8"),
            status=403,
            content_type="text/plain; charset=utf-8",
        )
    multi = bool(result.policy and len(result.policy.declared_regions) > 1)
    vary_target = bool(result.policy and (result.policy.vary_on_target or multi))
    _merge_vary(headers, include_target=vary_target)
    _apply_auth_cache_headers(headers, authenticated=authenticated)
    body = ""
    if node is not None:
        selected_mode = mode or RenderMode.FRAGMENT
        rendered = _render_body(
            node,
            request=request,
            context=context,
            mode=selected_mode,
            skip_prepare=skip_prepare,
        )
        body = rendered.html
        if selected_mode is RenderMode.PAGE:
            body = _inject_page_html(
                body,
                selected_mode,
                theme=_render_theme(rendered),
                plan=getattr(rendered, "htmx_plan", None),
                assets=rendered.assets,
            )
    return HttpResponse(
        body.encode("utf-8"),
        status=result.status_code,
        content_type="text/html; charset=utf-8",
        headers=headers,
    )
