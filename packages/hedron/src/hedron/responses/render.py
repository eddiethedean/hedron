"""Render NodeLike and InteractionResult values into HTML responses."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import Response as StarletteResponse

from hedron.htmx import approved_headers, render_mode_for_request
from hedron.responses.assets import (
    _attach_manifest_assets,
    _ensure_htmx_asset,
    _inject_build_assets,
    _inject_htmx_extension_assets,
)
from hedron.responses.html import (
    HTML,
    ComponentResponse,
    FragmentResponse,
    PageResponse,
)
from hedron.security.policy import SecurityPolicy
from hedron_core.builtins.document import Page
from hedron_core.component import NodeLike
from hedron_core.interaction import (
    FragmentRegion,
    FragmentRegionError,
    InteractionPolicy,
    InteractionResult,
    authorize_htmx_target,
    interaction_headers,
    materialize_interaction_nodes,
    select_htmx_auth_target,
    validated_extra_headers,
)
from hedron_core.rendering import RenderContext, RenderMode, RenderResult, render

__all__ = [
    "hedron_response",
    "merge_htmx_headers",
    "render_component_response",
    "render_interaction",
    "_apply_auth_cache_headers",
    "_fragment_region_http_detail",
]


def hedron_response(component_type: type[object] | None = None) -> dict[str, object]:
    """OpenAPI metadata for plain FastAPI component routes."""
    description = "Hedron HTML response"
    if component_type is not None:
        description = f"Hedron HTML response ({component_type.__name__})"
    return {
        "response_class": ComponentResponse,
        "responses": {
            200: {
                "content": {"text/html": {"schema": {"type": "string"}}},
                "description": description,
            }
        },
        "response_model": None,
    }


def _fragment_value(value: NodeLike) -> NodeLike:
    """Avoid duplicating the document shell for HTMX fragment navigation."""
    if isinstance(value, Page):
        children = list(value._children)
        if len(children) == 1:
            return children[0]  # type: ignore[no-any-return]
        return children  # type: ignore[return-value]
    return value


def _normalize_fragment_regions(
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
    request: Request,
    *,
    fragment_regions: tuple[FragmentRegion, ...],
    allow_undeclared_targets: bool = False,
    target: str | None = None,
) -> None:
    is_htmx = (request.headers.get("HX-Request") or "").lower() == "true"
    if not is_htmx:
        return
    target = request.headers.get("HX-Target") if target is None else target
    history_restore = (request.headers.get("HX-History-Restore-Request") or "").lower() == "true"
    from hedron_core.updates import matches_declared_host

    handle_hosts = tuple(
        region
        for region in fragment_regions
        if region.id.startswith("h-view-") or region.selector.startswith("#h-view-")
    )
    if handle_hosts:
        if not target:
            return
        if any(matches_declared_host(region, target) for region in handle_hosts):
            return
        raise FragmentRegionError(
            f"HX-Target {target!r} disagrees with owned handle host",
            requested=target,
            declared=tuple(region.selector for region in handle_hosts),
        )
    authorize_htmx_target(
        InteractionPolicy(
            declared_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
        ),
        target,
        is_htmx=True,
        history_restore=history_restore,
    )


def _apply_auth_cache_headers(headers: dict[str, str], *, authenticated: bool) -> None:
    if authenticated:
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


def render_component_response(
    value: NodeLike | HTML | RenderResult,
    *,
    request: Request | None = None,
    context: RenderContext | None = None,
    mode: RenderMode | None = None,
    policy: SecurityPolicy | None = None,
    authenticated: bool = False,
    extra_headers: Mapping[str, str] | None = None,
    status_code: int = 200,
    background: BackgroundTask | None = None,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
    _authorized_htmx_target: str | None = None,
) -> ComponentResponse:
    from fastapi import HTTPException

    regions = _normalize_fragment_regions(fragment_regions)
    if request is not None:
        try:
            _authorize_component_htmx(
                request,
                fragment_regions=regions,
                allow_undeclared_targets=allow_undeclared_targets,
                target=_authorized_htmx_target,
            )
        except FragmentRegionError as exc:
            from hedron_core.audit import SecurityAuditEventType, emit_security_audit

            emit_security_audit(
                SecurityAuditEventType.HTMX_TARGET_REJECTED,
                str(exc),
                attributes={
                    "path": str(request.url.path),
                    "target": request.headers.get("HX-Target"),
                },
            )
            raise HTTPException(
                status_code=403,
                detail=_fragment_region_http_detail(exc, request=request),
            ) from exc

    force_mode = mode
    if isinstance(value, HTML):
        force_mode = value.mode or force_mode
        value = value.value
    if isinstance(value, RenderResult):
        result = value
        selected_mode = result.mode
    else:
        if request is not None:
            result_policy = value.policy if isinstance(value, InteractionResult) else None
            selected_mode = render_mode_for_request(request, force=force_mode, policy=result_policy)
        else:
            selected_mode = force_mode or RenderMode.PAGE
        render_context = context
        if render_context is None and request is not None:
            from hedron.context import render_context_from_request

            render_context = render_context_from_request(request)
        render_context = render_context or RenderContext.standalone()
        to_render: NodeLike = value
        if selected_mode is RenderMode.FRAGMENT:
            to_render = _fragment_value(value)
        from hedron_core.htmx_eval import reset_htmx_eval_allowed, set_htmx_eval_allowed

        eval_token = set_htmx_eval_allowed(bool(policy and policy.allow_htmx_eval))
        try:
            result = render(to_render, context=render_context, mode=selected_mode)
        finally:
            reset_htmx_eval_allowed(eval_token)

    if request is not None:
        result = _attach_manifest_assets(result, request)

    headers = dict(result.headers)
    if policy is not None:
        headers.update(policy.response_headers(authenticated=authenticated))
    if extra_headers:
        headers.update(validated_extra_headers(extra_headers))
    _apply_auth_cache_headers(headers, authenticated=authenticated)

    response_cls: type[ComponentResponse] = (
        FragmentResponse if selected_mode is RenderMode.FRAGMENT else PageResponse
    )
    html_text = result.html
    if request is not None:
        html_text = _inject_build_assets(html_text, selected_mode, request, result)
    else:
        # Request-less PAGE paths still need extension order (#55).
        html_text = _ensure_htmx_asset(html_text, selected_mode, policy=policy)
        html_text = _inject_htmx_extension_assets(
            html_text, request=None, plan=getattr(result, "htmx_plan", None)
        )
    return response_cls(
        content=html_text,
        status_code=status_code,
        headers=headers,
        background=background,
    )


merge_htmx_headers = approved_headers


def _fragment_region_http_detail(
    exc: FragmentRegionError, *, request: Request
) -> str | dict[str, object]:
    """Production stays opaque; non-production includes HED-HTMX diagnostics."""
    app = request.scope.get("app")
    production = bool(getattr(getattr(app, "state", None), "hedron_production", False))
    if production:
        return "HX-Target is not an authorized fragment region"
    from hedron_core.codes import HED_HTMX_0001
    from hedron_core.diagnostics import DiagnosticSeverity, make_diagnostic

    code = getattr(exc, "code", None) or HED_HTMX_0001
    requested = getattr(exc, "requested", None)
    declared = list(getattr(exc, "declared", ()) or ())
    diagnostic = make_diagnostic(
        code,
        severity=DiagnosticSeverity.ERROR,
        title="Unauthorized HTMX target",
        explanation=str(exc),
        remediation=(
            "Declare the target via fragment_regions= / @app.fragment(region=...), "
            "or fix the control's hx-target / RefreshButton.for_region(...)."
        ),
        context={"requested": requested, "declared": declared, "path": str(request.url.path)},
    )
    return {
        "code": diagnostic.code,
        "title": diagnostic.title,
        "explanation": diagnostic.explanation,
        "remediation": diagnostic.remediation,
        "requested": requested,
        "declared": declared,
    }


async def render_interaction(
    request: Request,
    result: InteractionResult,
    *,
    policy: SecurityPolicy | None = None,
    authenticated: bool | None = None,
    fragment_regions: tuple[FragmentRegion, ...] = (),
    mode: RenderMode | None = None,
    kind: str = "page",
    allow_undeclared_targets: bool = False,
) -> StarletteResponse:
    """Public InteractionResult → Response conversion (RFC-0044 / #35).

    Prefer this over ``HedronRoute._convert_interaction_result``. Honors caller-supplied
    ``SecurityPolicy`` and the result's ``InteractionPolicy`` (including apps that disable
    CSRF or own response headers).
    """
    from fastapi import HTTPException

    from hedron.context import render_context_from_request
    from hedron.security.csrf import ensure_csrf_cookie
    from hedron_core.interaction import apply_allow_undeclared_targets, merge_route_regions

    sec = policy
    if sec is None:
        sec = getattr(request.app.state, "hedron_security", SecurityPolicy.from_name("standard"))
    auth = (
        bool(getattr(request.state, "hedron_authenticated", False))
        if authenticated is None
        else authenticated
    )

    result = apply_allow_undeclared_targets(result, allow_undeclared_targets)
    if fragment_regions:
        result = merge_route_regions(result, fragment_regions)

    target = request.headers.get("HX-Target")
    is_htmx = (request.headers.get("HX-Request") or "").lower() == "true"
    history_restore = (request.headers.get("HX-History-Restore-Request") or "").lower() == "true"
    try:
        auth_target = select_htmx_auth_target(client_target=target, region_id=result.region_id)
        region = authorize_htmx_target(
            result.policy,
            auth_target,
            is_htmx=is_htmx,
            history_restore=history_restore,
        )
    except FragmentRegionError as exc:
        from hedron_core.audit import SecurityAuditEventType, emit_security_audit

        emit_security_audit(
            SecurityAuditEventType.HTMX_TARGET_REJECTED,
            str(exc),
            attributes={"path": str(request.url.path), "target": target},
        )
        raise HTTPException(
            status_code=403,
            detail=_fragment_region_http_detail(exc, request=request),
        ) from exc

    if result.status_code == 204 and result.oob:
        raise HTTPException(
            status_code=403,
            detail="OOB updates are not allowed on 204 InteractionResult responses",
        )

    content: NodeLike | None = result.content
    if result.oob:
        try:
            content = materialize_interaction_nodes(result)
        except (FragmentRegionError, ValueError, TypeError) as exc:
            if isinstance(exc, FragmentRegionError):
                raise HTTPException(
                    status_code=403,
                    detail=_fragment_region_http_detail(exc, request=request),
                ) from exc
            raise HTTPException(status_code=403, detail=str(exc)) from exc

    try:
        headers = interaction_headers(result)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    if region is not None and result.policy and result.policy.vary_on_target:
        existing = {p.strip() for p in headers.get("Vary", "").split(",") if p.strip()}
        existing.update({"HX-Request", "HX-History-Restore-Request", "HX-Target"})
        headers["Vary"] = ", ".join(sorted(existing))

    force = mode
    if kind == "component":
        force = force or RenderMode.FRAGMENT
    if result.status_code == 204 or (result.content is None and result.status_code == 204):
        # Auth already ran; 204 has no primary body — still seed CSRF on safe methods.
        _apply_auth_cache_headers(headers, authenticated=auth)
        response = StarletteResponse(status_code=204, headers=headers)
        if sec.csrf_enabled and request.method.upper() in {"GET", "HEAD"}:
            ensure_csrf_cookie(response, sec, request=request)
        return response
    if content is None:
        _apply_auth_cache_headers(headers, authenticated=auth)
        response = StarletteResponse(status_code=result.status_code, headers=headers)
        if sec.csrf_enabled and request.method.upper() in {"GET", "HEAD"}:
            ensure_csrf_cookie(response, sec, request=request)
        return response

    from hedron.routing.route import _prepare_endpoint_value

    await _prepare_endpoint_value(content, request=request)
    response = render_component_response(
        content,
        request=request,
        context=render_context_from_request(request),
        mode=force,
        policy=sec,
        authenticated=auth,
        extra_headers=headers,
        status_code=result.status_code,
        fragment_regions=(result.policy.declared_regions if result.policy is not None else ())
        or fragment_regions,
        allow_undeclared_targets=allow_undeclared_targets
        or bool(result.policy and result.policy.allow_undeclared_targets),
        _authorized_htmx_target=auth_target,
    )
    if sec.csrf_enabled and request.method.upper() in {"GET", "HEAD"}:
        ensure_csrf_cookie(response, sec, request=request)
    return response
