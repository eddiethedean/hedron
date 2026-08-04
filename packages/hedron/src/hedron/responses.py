"""Component HTML response helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from fastapi.responses import HTMLResponse
from starlette.background import BackgroundTask
from starlette.requests import Request

from hedron.htmx import approved_headers, render_mode_for_request
from hedron.security.policy import SecurityPolicy
from hedron_core.builtins.document import Page
from hedron_core.component import Component, NodeLike
from hedron_core.rendering import RenderContext, RenderMode, RenderResult, render

__all__ = [
    "ComponentResponse",
    "FileComponentResponse",
    "FragmentResponse",
    "HTML",
    "PageResponse",
    "hedron_response",
    "render_component_response",
]


class HTML:
    """Explicit HTML intent wrapper for plain FastAPI routes."""

    __slots__ = ("value", "mode")

    def __init__(self, value: NodeLike | Component[Any], *, mode: RenderMode | None = None) -> None:
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


def hedron_response(component_type: type[Any] | None = None) -> dict[str, Any]:
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


def _fragment_value(value: NodeLike | Component[Any]) -> NodeLike | Component[Any]:
    """Avoid duplicating the document shell for HTMX fragment navigation."""
    if isinstance(value, Page):
        children = list(value._children)
        if len(children) == 1:
            return children[0]  # type: ignore[no-any-return]
        return children  # type: ignore[return-value]
    return value


def render_component_response(
    value: NodeLike | Component[Any] | HTML | RenderResult,
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
        to_render: NodeLike | Component[Any] = value
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
        html_text = _ensure_htmx_asset(html_text, selected_mode)
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

    html_text = _ensure_htmx_asset(html_text, mode)
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
    if not tags:
        return html_text
    injection = "\n".join(tags)
    if "</head>" in html_text:
        return html_text.replace("</head>", f"{injection}\n</head>", 1)
    if "</body>" in html_text:
        return html_text.replace("</body>", f"{injection}\n</body>", 1)
    return html_text + injection


def _ensure_htmx_asset(html_text: str, mode: RenderMode) -> str:
    """Inject the bundled HTMX runtime and Hedron's secure v2 defaults."""
    if mode is not RenderMode.PAGE:
        return html_text
    config = (
        '<meta name="htmx-config" '
        "content='{"
        '"allowEval":false,'
        '"allowScriptTags":false,'
        '"historyRestoreAsHxRequest":false,'
        '"includeIndicatorStyles":false,'
        '"reportValidityOfForms":true,'
        '"selfRequestsOnly":true'
        "}'>"
    )
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


def merge_htmx_headers(**kwargs: Any) -> dict[str, str]:
    return approved_headers(**kwargs)
