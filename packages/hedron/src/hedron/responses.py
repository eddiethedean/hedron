"""Component HTML response helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from fastapi.responses import HTMLResponse
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import Response as StarletteResponse

from hedron.htmx import approved_headers, render_mode_for_request
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
    "ComponentResponse",
    "FileComponentResponse",
    "FragmentResponse",
    "HTML",
    "PageResponse",
    "hedron_response",
    "merge_htmx_headers",
    "render_component_response",
    "render_interaction",
]


class HTML:
    """Explicit HTML intent wrapper for plain FastAPI routes."""

    __slots__ = ("value", "mode")

    def __init__(self, value: NodeLike, *, mode: RenderMode | None = None) -> None:
        self.value = value
        self.mode = mode


class ComponentResponse(HTMLResponse):
    media_type = "text/html"


class PageResponse(ComponentResponse):
    pass


class FragmentResponse(ComponentResponse):
    pass


class FileComponentResponse(ComponentResponse):
    """File/download results produced through safe source contracts."""

    def __init__(
        self,
        content: str | bytes,
        *,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str = "application/octet-stream",
        filename: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        hdrs = dict(headers or {})
        if filename:
            safe_name = _safe_content_disposition_filename(filename)
            hdrs.setdefault("Content-Disposition", f'attachment; filename="{safe_name}"')
        super().__init__(
            content=content,
            status_code=status_code,
            headers=hdrs,
            media_type=media_type,
            background=background,
        )


def _safe_content_disposition_filename(filename: str) -> str:
    from hedron.builtins.files import validate_upload_filename

    try:
        return validate_upload_filename(filename)[:200]
    except ValueError:
        return "download"


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
) -> None:
    is_htmx = (request.headers.get("HX-Request") or "").lower() == "true"
    if not is_htmx:
        return
    target = request.headers.get("HX-Target")
    history_restore = (request.headers.get("HX-History-Restore-Request") or "").lower() == "true"
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
) -> ComponentResponse:
    from fastapi import HTTPException

    regions = _normalize_fragment_regions(fragment_regions)
    if request is not None:
        try:
            _authorize_component_htmx(
                request,
                fragment_regions=regions,
                allow_undeclared_targets=allow_undeclared_targets,
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
            selected_mode = render_mode_for_request(request, force=force_mode)
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
        result = render(to_render, context=render_context, mode=selected_mode)

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
        html_text = _inject_htmx_extension_assets(html_text, request=None)
    return response_cls(
        content=html_text,
        status_code=status_code,
        headers=headers,
        background=background,
    )


def _attach_manifest_assets(result: RenderResult, request: Request) -> RenderResult:
    """Populate ``result.assets`` from the active build manifest when empty."""
    if result.assets:
        return result
    manifest = getattr(request.app.state, "hedron_build_manifest", None)
    if manifest is None:
        return result
    from dataclasses import replace
    from types import MappingProxyType

    from hedron_core.rendering import AssetRef

    assets_prefix = getattr(request.app.state, "hedron_assets_path", "/hedron-assets")
    attached: list[AssetRef] = []
    for entry in manifest.assets.assets:
        href = f"{assets_prefix.rstrip('/')}/{entry.path}"
        attached.append(
            AssetRef(
                kind=entry.kind,
                href=href,
                attributes=MappingProxyType(dict(entry.attributes)),
            )
        )
    if not attached:
        return result
    return replace(result, assets=tuple(attached))


def _mounted_static_href(path: str, request: Request | None) -> str:
    """Prefix a local static path with the app mount when configured."""
    href = path if path.startswith("/") else f"/{path}"
    if request is None:
        return href
    from hedron.mount import mount_from_request, prefix_local_path

    mount = getattr(request.app.state, "hedron_mount_path", None)
    if not isinstance(mount, str):
        mount = mount_from_request(request).path
    return prefix_local_path(href, mount)


def _inject_build_assets(
    html_text: str,
    mode: RenderMode,
    request: Request,
    result: RenderResult,
) -> str:
    import html as html_lib

    policy = getattr(request.app.state, "hedron_security", None)
    if not isinstance(policy, SecurityPolicy):
        policy = SecurityPolicy.from_name("standard")
    html_text = _ensure_htmx_asset(html_text, mode, policy=policy, request=request)
    if mode is not RenderMode.PAGE:
        return html_text
    tags: list[str] = []
    seen: set[str] = set()

    def add(tag: str) -> None:
        if tag in html_text or tag in seen:
            return
        seen.add(tag)
        tags.append(tag)

    if getattr(request.app.state, "hedron_default_styles", True):
        css = _mounted_static_href("/hedron-static/hedron-default.css", request)
        add(f'<link rel="stylesheet" href="{css}">')

    for asset in result.assets:
        href = html_lib.escape(asset.href, quote=True)
        if asset.kind == "css":
            add(f'<link rel="stylesheet" href="{href}">')
        elif asset.kind in {"js", "module"}:
            typ = ' type="module"' if asset.kind == "module" else ""
            add(f'<script{typ} src="{href}"></script>')
    # Always offer bundled disclose module from package static for WC proof
    if "hedron-disclose.mjs" not in html_text:
        disclose = _mounted_static_href("/hedron-static/hedron-disclose.mjs", request)
        add(f'<script type="module" src="{disclose}"></script>')
    if "hedron-ui.mjs" not in html_text:
        ui = _mounted_static_href("/hedron-static/hedron-ui.mjs", request)
        add(f'<script type="module" src="{ui}"></script>')
    if tags:
        injection = "\n".join(tags)
        if "</head>" in html_text:
            html_text = html_text.replace("</head>", f"{injection}\n</head>", 1)
        elif "</body>" in html_text:
            html_text = html_text.replace("</body>", f"{injection}\n</body>", 1)
        else:
            html_text = html_text + injection
    # Pin bundled HTMX extensions immediately after the core runtime so deferred
    # scripts execute in dependency order (issue #55 / RFC-0032).
    return _inject_htmx_extension_assets(html_text, request)


def _htmx_core_script_end(html_text: str) -> int | None:
    """Return the index immediately after the HTMX core ``</script>`` tag, if present."""
    from hedron_core.page_assets import htmx_core_script_end

    return htmx_core_script_end(html_text)


def _inject_htmx_extension_assets(html_text: str, request: Request | None) -> str:
    """Insert non-deferred HTMX extensions after the core runtime script."""
    from hedron_core.page_assets import inject_htmx_extensions

    def _href(path: str) -> str:
        return _mounted_static_href(path, request)

    return inject_htmx_extensions(html_text, static_href=_href)


def _ensure_htmx_asset(
    html_text: str,
    mode: RenderMode,
    *,
    policy: SecurityPolicy | None = None,
    request: Request | None = None,
) -> str:
    """Inject the bundled HTMX runtime and profile-driven secure v2 defaults."""
    from hedron_core.page_assets import inject_htmx_core

    def _href(path: str) -> str:
        return _mounted_static_href(path, request)

    return inject_htmx_core(html_text, mode, policy=policy, static_href=_href)


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
    from hedron.interaction import merge_route_regions
    from hedron.security.csrf import ensure_csrf_cookie
    from hedron_core.interaction import apply_allow_undeclared_targets

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
    )
    if sec.csrf_enabled and request.method.upper() in {"GET", "HEAD"}:
        ensure_csrf_cookie(response, sec, request=request)
    return response
