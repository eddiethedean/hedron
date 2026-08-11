"""Build Flask responses from Hedron components and InteractionResult values."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from flask import Response
from flask import request as flask_request

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
from hedron_flask.htmx import render_mode_for_request

__all__ = [
    "component_response",
    "interaction_response",
]


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
        path = ""
        try:
            path = str(getattr(flask_request, "path", "") or "")
        except RuntimeError:
            path = ""
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


def _default_render_context() -> RenderContext:
    """Build RenderContext with CSRF material when a HedronFlask extension is bound."""
    try:
        from flask import current_app, has_request_context, request
    except Exception:  # noqa: BLE001
        return RenderContext.standalone()
    if not has_request_context():
        return RenderContext.standalone()
    extension = current_app.extensions.get("hedron")
    csrf_token: str | None = None
    csrf_form_field = "csrf_token"
    policy = getattr(extension, "security_policy", None) if extension is not None else None
    from hedron_core.security_policy import SecurityPolicy

    if isinstance(policy, SecurityPolicy) and policy.csrf_enabled:
        strategy = policy.resolve_csrf_strategy()
        if strategy is not None:
            csrf_form_field = strategy.form_field
            from hedron_flask.csrf import csrf_token_for_request

            cookie_name = getattr(extension, "csrf_cookie_name", "hedron_csrf")
            csrf_token = csrf_token_for_request(
                request,
                cookie_name=str(cookie_name),
                policy=policy,
            )
    return RenderContext.standalone(csrf_token=csrf_token, csrf_form_field=csrf_form_field)


def _render_body(
    value: NodeLike | Component[Any] | RenderResult,
    *,
    headers: Mapping[str, str] | None = None,
    context: RenderContext | None = None,
    mode: RenderMode | None = None,
    skip_prepare: bool = False,
) -> RenderResult:
    if isinstance(value, RenderResult):
        return value
    _maybe_prepare(value, skip_prepare=skip_prepare)
    hdrs = dict(headers) if headers is not None else dict(flask_request.headers)
    selected_mode = render_mode_for_request(hdrs, force=mode)
    render_context = context or _default_render_context()
    to_render: NodeLike | Component[Any] = value
    if selected_mode is RenderMode.FRAGMENT:
        to_render = _fragment_value(value)
    return render(to_render, context=render_context, mode=selected_mode)


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
        # Fragment/HTMX responses must not remain publicly cacheable.
        existing = headers.get("Cache-Control", "")
        lowered = existing.lower()
        if "public" in lowered or not existing:
            headers["Cache-Control"] = "private, no-store"


def _security_policy_from_app() -> SecurityPolicy:
    try:
        from flask import current_app

        ext = current_app.extensions.get("hedron")
        policy = getattr(ext, "security_policy", None)
        if isinstance(policy, SecurityPolicy):
            return policy
    except RuntimeError:
        pass
    return SecurityPolicy.from_name("standard")


def _flask_static_href(path: str) -> str:
    href = path if path.startswith("/") else f"/{path}"
    try:
        script_root = getattr(flask_request, "script_root", "") or ""
    except RuntimeError:
        script_root = ""
    mount = normalize_mount_path(str(script_root))
    return prefix_local_path(href, mount)


def _inject_page_html(html_text: str, mode: RenderMode) -> str:
    return inject_page_assets(
        html_text,
        mode,
        policy=_security_policy_from_app(),
        static_href=_flask_static_href,
    )


def component_response(
    value: NodeLike | Component[Any] | RenderResult,
    *,
    status_code: int = 200,
    context: RenderContext | None = None,
    mode: RenderMode | None = None,
    extra_headers: Mapping[str, str] | None = None,
    headers_map: Mapping[str, str] | None = None,
    authenticated: bool = False,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
    skip_prepare: bool = False,
) -> Response:
    if headers_map is not None:
        hdrs: Mapping[str, str] = headers_map
    else:
        hdrs = dict(flask_request.headers)
    try:
        _authorize_component_htmx(
            headers_map=hdrs,
            fragment_regions=_normalize_regions(fragment_regions),
            allow_undeclared_targets=allow_undeclared_targets,
        )
    except FragmentRegionError as exc:
        return Response(str(exc), status=403, mimetype="text/plain")
    result = _render_body(
        value, headers=hdrs, context=context, mode=mode, skip_prepare=skip_prepare
    )
    headers = dict(result.headers)
    _merge_vary(headers)
    _apply_auth_cache_headers(headers, authenticated=authenticated)
    if extra_headers:
        try:
            headers.update(validated_extra_headers(extra_headers))
        except ValueError as exc:
            return Response(str(exc), status=403, mimetype="text/plain")
        _apply_auth_cache_headers(headers, authenticated=authenticated)
    selected_mode = render_mode_for_request(hdrs, force=mode)
    body = _inject_page_html(result.html, selected_mode)
    return Response(body, status=status_code, mimetype="text/html", headers=headers)


def interaction_response(
    result: InteractionResult,
    *,
    context: RenderContext | None = None,
    mode: RenderMode | None = None,
    extra_headers: Mapping[str, str] | None = None,
    headers_map: Mapping[str, str] | None = None,
    authenticated: bool = False,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
    skip_prepare: bool = False,
) -> Response:
    from hedron_core.interaction import apply_allow_undeclared_targets

    if headers_map is not None:
        hdrs: Mapping[str, str] = headers_map
    else:
        hdrs = dict(flask_request.headers)
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
        path = ""
        try:
            path = str(getattr(flask_request, "path", "") or "")
        except RuntimeError:
            path = ""
        emit_security_audit(
            SecurityAuditEventType.HTMX_TARGET_REJECTED,
            str(exc),
            attributes={
                "path": path,
                "target": client_target,
            },
        )
        return Response(str(exc), status=403, mimetype="text/plain")
    multi = bool(result.policy and len(result.policy.declared_regions) > 1)
    vary_target = bool(result.policy and (result.policy.vary_on_target or multi))
    _merge_vary(headers, include_target=vary_target)
    _apply_auth_cache_headers(headers, authenticated=authenticated)
    body = ""
    if node is not None:
        rendered = _render_body(
            node,
            headers=headers_map,
            context=context,
            mode=mode or RenderMode.FRAGMENT,
            skip_prepare=skip_prepare,
        )
        body = rendered.html
    return Response(
        body,
        status=result.status_code,
        mimetype="text/html",
        headers=headers,
    )
