"""Component HTML response helpers."""

from __future__ import annotations

from collections.abc import Mapping

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
    InteractionResult,
    authorize_htmx_target,
    interaction_headers,
    materialize_interaction_nodes,
    select_htmx_auth_target,
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
    cleaned = filename.replace("\r", "").replace("\n", "").replace('"', "").replace("\\", "")
    cleaned = cleaned.strip() or "download"
    return cleaned[:200]


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
) -> ComponentResponse:
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
        headers.update(extra_headers)

    response_cls: type[ComponentResponse] = (
        FragmentResponse if selected_mode is RenderMode.FRAGMENT else PageResponse
    )
    html_text = result.html
    if request is not None:
        html_text = _inject_build_assets(html_text, selected_mode, request, result)
    else:
        html_text = _ensure_htmx_asset(html_text, selected_mode, policy=policy)
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
    html_text = _ensure_htmx_asset(html_text, mode, policy=policy)
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
        add('<link rel="stylesheet" href="/hedron-static/hedron-default.css">')

    for asset in result.assets:
        href = html_lib.escape(asset.href, quote=True)
        if asset.kind == "css":
            add(f'<link rel="stylesheet" href="{href}">')
        elif asset.kind in {"js", "module"}:
            typ = ' type="module"' if asset.kind == "module" else ""
            add(f'<script{typ} src="{href}"></script>')
    # Always offer bundled disclose module from package static for WC proof
    if "hedron-disclose.mjs" not in html_text:
        add('<script type="module" src="/hedron-static/hedron-disclose.mjs"></script>')
    if "hedron-ui.mjs" not in html_text:
        add('<script type="module" src="/hedron-static/hedron-ui.mjs"></script>')
    # Pin non-deferred HTMX extensions after the core runtime (RFC-0032).
    from hedron_core.htmx_extensions import known_extensions

    for ext in sorted(known_extensions(), key=lambda e: e.load_order):
        if ext.deferred:
            continue
        if ext.path in html_text:
            continue
        add(f'<script src="{ext.path}" defer></script>')
    if not tags:
        return html_text
    injection = "\n".join(tags)
    if "</head>" in html_text:
        return html_text.replace("</head>", f"{injection}\n</head>", 1)
    if "</body>" in html_text:
        return html_text.replace("</body>", f"{injection}\n</body>", 1)
    return html_text + injection


def _ensure_htmx_asset(
    html_text: str,
    mode: RenderMode,
    *,
    policy: SecurityPolicy | None = None,
) -> str:
    """Inject the bundled HTMX runtime and profile-driven secure v2 defaults."""
    if mode is not RenderMode.PAGE:
        return html_text
    sec = policy or SecurityPolicy.from_name("standard")
    if sec.htmx_browser_preset:
        config = f"<meta name=\"htmx-config\" content='{sec.htmx_config_json()}'>"
        if 'name="htmx-config"' not in html_text and "name='htmx-config'" not in html_text:
            if "</head>" in html_text:
                html_text = html_text.replace("</head>", f"{config}</head>", 1)
            else:
                html_text = config + html_text
    tag = '<script src="/hedron-static/htmx.min.js" defer></script>'
    if "htmx.min.js" in html_text:
        return html_text
    if "</body>" in html_text:
        return html_text.replace("</body>", f"{tag}</body>", 1)
    return html_text + tag


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

    sec = policy
    if sec is None:
        sec = getattr(request.app.state, "hedron_security", SecurityPolicy.from_name("standard"))
    auth = (
        bool(getattr(request.state, "hedron_authenticated", False))
        if authenticated is None
        else authenticated
    )

    if fragment_regions:
        result = merge_route_regions(result, fragment_regions)

    if result.status_code == 204 or (result.content is None and result.status_code == 204):
        try:
            headers = interaction_headers(result)
        except ValueError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        return StarletteResponse(status_code=204, headers=headers)

    target = request.headers.get("HX-Target")
    is_htmx = (request.headers.get("HX-Request") or "").lower() == "true"
    try:
        auth_target = select_htmx_auth_target(client_target=target, region_id=result.region_id)
        region = authorize_htmx_target(
            result.policy,
            auth_target,
            is_htmx=is_htmx,
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

    content: NodeLike | None = result.content
    if result.oob:
        try:
            content = materialize_interaction_nodes(result)
        except (FragmentRegionError, ValueError) as exc:
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
    if content is None:
        return StarletteResponse(status_code=result.status_code, headers=headers)

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
    )
    if sec.csrf_enabled and request.method.upper() in {"GET", "HEAD"}:
        ensure_csrf_cookie(response, sec, request=request)
    return response
