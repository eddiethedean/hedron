"""HTMX and static asset injection for HTML responses."""

from __future__ import annotations

from starlette.requests import Request

from hedron.security.policy import SecurityPolicy
from hedron_core.rendering import RenderMode, RenderResult

__all__ = [
    "_attach_manifest_assets",
    "_ensure_htmx_asset",
    "_htmx_core_script_end",
    "_inject_build_assets",
    "_inject_htmx_extension_assets",
    "_mounted_static_href",
]


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
    configured = bool(getattr(request.app.state, "hedron_mount_was_configured", False))
    if not isinstance(mount, str) or (not mount and not configured):
        mount = mount_from_request(request).path
    return prefix_local_path(href, mount)


def _inject_build_assets(
    html_text: str,
    mode: RenderMode,
    request: Request,
    result: RenderResult,
) -> str:
    import html as html_lib

    from hedron_core.page_assets import inject_alpine_plan, inject_htmx_bridge, inject_page_theme

    policy = getattr(request.app.state, "hedron_security", None)
    if not isinstance(policy, SecurityPolicy):
        policy = SecurityPolicy.from_name("standard")
    trace_theme = result.trace.get("theme") if result.trace is not None else None
    theme = trace_theme if isinstance(trace_theme, str) else None
    html_text = inject_page_theme(html_text, mode, theme)
    demand_driven = bool(getattr(request.app.state, "hedron_demand_driven_assets", False))
    requires_htmx = bool(getattr(result, "requires_htmx", False))
    html_text = _ensure_htmx_asset(
        html_text,
        mode,
        policy=policy,
        request=request,
        required=requires_htmx if demand_driven else None,
    )
    if requires_htmx:
        html_text = inject_htmx_bridge(
            html_text,
            mode,
            static_href=lambda path: _mounted_static_href(path, request),
        )
    html_text = inject_alpine_plan(
        html_text,
        mode,
        getattr(result, "browser_plan", None),
        static_href=lambda path: _mounted_static_href(path, request),
    )
    if mode is not RenderMode.PAGE:
        from hedron_core.head_support import reject_invented_fragment_scripts

        reject_invented_fragment_scripts(html_text)
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
        href = html_lib.escape(_mounted_static_href(asset.href, request), quote=True)
        if asset.kind == "css":
            add(f'<link rel="stylesheet" href="{href}">')
        elif asset.kind in {"js", "module"}:
            typ = ' type="module"' if asset.kind == "module" else ""
            add(f'<script{typ} src="{href}"></script>')
    ui_demand = any(
        marker in html_text
        for marker in (
            "hedron-tabs",
            "data-hedron-password-toggle",
            "data-hedron-toast",
            "data-hedron-reveal",
            "data-hedron-nav-toggle",
            "data-hedron-after-load",
        )
    )
    disclose_demand = "<hedron-" in html_text
    if (not demand_driven or disclose_demand) and "hedron-disclose.mjs" not in html_text:
        disclose = _mounted_static_href("/hedron-static/hedron-disclose.mjs", request)
        add(f'<script type="module" src="{disclose}"></script>')
    if (not demand_driven or ui_demand) and "hedron-ui.mjs" not in html_text:
        ui = _mounted_static_href("/hedron-static/hedron-ui.mjs", request)
        add(f'<script type="module" src="{ui}"></script>')
    mount = _mounted_static_href("/", request).removesuffix("/")
    if mount and 'name="hedron-mount-path"' not in html_text:
        safe_mount = html_lib.escape(mount, quote=True)
        add(f'<meta name="hedron-mount-path" content="{safe_mount}">')
    if mount and "hedron-mount.mjs" not in html_text:
        runtime = _mounted_static_href("/hedron-static/hedron-mount.mjs", request)
        add(f'<script type="module" src="{runtime}"></script>')
    if tags:
        injection = "\n".join(tags)
        if "</head>" in html_text:
            html_text = html_text.replace("</head>", f"{injection}\n</head>", 1)
        elif "</body>" in html_text:
            html_text = html_text.replace("</body>", f"{injection}\n</body>", 1)
        else:
            html_text = html_text + injection
    from hedron_core.head_support import merge_registered_head
    from hedron_core.htmx_extensions import ExtensionPlan

    plan = getattr(result, "htmx_plan", None)
    enabled = isinstance(plan, ExtensionPlan) and "head-support" in plan.ids
    html_text = merge_registered_head(
        html_text,
        result.assets,
        enabled=enabled and (not demand_driven or requires_htmx),
    )
    # Pin bundled HTMX extensions immediately after the core runtime so deferred
    # scripts execute in dependency order (issue #55 / RFC-0032).
    if demand_driven and not requires_htmx:
        return html_text
    return _inject_htmx_extension_assets(html_text, request, plan)


def _htmx_core_script_end(html_text: str) -> int | None:
    """Return the index immediately after the HTMX core ``</script>`` tag, if present."""
    from hedron_core.page_assets import htmx_core_script_end

    return htmx_core_script_end(html_text)


def _inject_htmx_extension_assets(
    html_text: str,
    request: Request | None,
    plan: object | None = None,
) -> str:
    """Insert planned HTMX extensions after the core runtime script."""
    from hedron_core.htmx_extensions import ExtensionPlan
    from hedron_core.page_assets import inject_htmx_extensions

    def _href(path: str) -> str:
        return _mounted_static_href(path, request)

    resolved = plan if isinstance(plan, ExtensionPlan) else None
    return inject_htmx_extensions(html_text, static_href=_href, plan=resolved)


def _ensure_htmx_asset(
    html_text: str,
    mode: RenderMode,
    *,
    policy: SecurityPolicy | None = None,
    request: Request | None = None,
    required: bool | None = None,
) -> str:
    """Inject the bundled HTMX runtime and profile-driven secure v2 defaults."""
    from hedron_core.page_assets import inject_htmx_core

    def _href(path: str) -> str:
        return _mounted_static_href(path, request)

    if required is False:
        return html_text
    return inject_htmx_core(html_text, mode, policy=policy, static_href=_href)
