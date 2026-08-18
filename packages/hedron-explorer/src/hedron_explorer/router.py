"""Component Explorer router with HTMX panels (phase 0.4)."""

from __future__ import annotations

import html as html_lib
import logging
import time
from collections import deque
from pathlib import Path
from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from hedron_core.catalog import InteractionCatalog, compile_interaction_catalog, get_sealed_catalog
from hedron_core.dashboard import dashboard_graph_payload
from hedron_core.plugins import get_explorer_panels
from hedron_core.registry import ComponentMeta, get_registry
from hedron_core.rendering import RenderMode, render
from hedron_core.typing_aliases import JsonObject, JsonValue

__all__ = ["explorer_router"]

_logger = logging.getLogger("hedron.explorer")
_TRACE: deque[JsonObject] = deque(maxlen=100)
_RATE: dict[str, list[float]] = {}
_AUDIT: deque[JsonObject] = deque(maxlen=200)
_SIMULATE_KEYS = frozenset(
    {
        "route",
        "allow_mutations",
        "mode",
        "target",
        "boosted",
        "history_restore",
        "status",
    }
)


def _redact(value: str | None) -> str | None:
    if value is None:
        return None
    if "/" in value or "\\" in value:
        return Path(value).name
    return value


def _app_catalog(app: object) -> InteractionCatalog:
    cached = getattr(getattr(app, "state", None), "hedron_interactions", None)
    if isinstance(cached, InteractionCatalog):
        return cached
    live = get_sealed_catalog()
    if live is not None:
        return live
    return compile_interaction_catalog()


def _handle_graph_html(request: Request) -> str:
    from hedron_core.updates import handle_graph_payload

    app_id = str(getattr(getattr(request.app, "state", None), "hedron_app_id", "") or "")
    payload = handle_graph_payload(app_id=app_id or None)
    nodes = payload.get("nodes") or []
    if not isinstance(nodes, list) or not nodes:
        return "<p>No refreshable views or commands registered.</p>"
    rows = []
    for node in nodes:
        if not isinstance(node, dict):
            continue
        kind = html_lib.escape(str(node.get("kind", "")))
        effect = html_lib.escape(str(node.get("effect", "dynamic")))
        ident = html_lib.escape(str(node.get("id", "")))
        path = html_lib.escape(str(node.get("path", "")))
        rows.append(f"<tr><td>{ident}</td><td>{kind}</td><td>{effect}</td><td>{path}</td></tr>")
    body = "".join(rows)
    return (
        "<p>Command effects are labeled <code>dynamic</code> or <code>observed</code>, "
        "never declared.</p>"
        "<table><thead><tr><th>Handle</th><th>Kind</th><th>Effect</th><th>Path</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


def _audit(event: str, **payload: JsonValue) -> None:
    _AUDIT.appendleft({"event": event, **payload, "ts": time.time()})


def _project_component_roots(request: Request | None) -> list[Path]:
    """Trusted roots only: app.state and [tool.hedron] component_roots."""
    roots: list[Path] = []
    if request is None:
        return roots
    configured = getattr(request.app.state, "hedron_component_roots", None)
    if configured:
        roots.extend(Path(p).resolve() for p in configured)
    project_root = getattr(request.app.state, "hedron_project_root", None)
    if project_root:
        try:
            loader = getattr(request.app.state, "hedron_settings_loader", None)
            if callable(loader):
                settings = loader(Path(project_root))
            else:
                # Optional: flagship config without hard-depending on `hedron`.
                from importlib import import_module

                mod = import_module("hedron.config")
                settings = mod.load_hedron_settings(Path(project_root))
            resolved = getattr(settings, "resolved_roots", None)
            if callable(resolved):
                extra = resolved(base=Path(project_root))
                if isinstance(extra, (list, tuple)):
                    roots.extend(Path(p) for p in extra)
        except Exception as exc:  # noqa: BLE001
            # Explorer stays available when optional config/settings fail to load.
            _logger.debug("Explorer component roots from settings unavailable: %s", exc)
    return roots


def _allowed_roots(meta: object, request: Request | None = None) -> list[Path]:
    """Allow reads under project component roots only.

    ``meta.folder_path`` is ignored as a root: registry metadata can be
    attacker-influenced when browsing components in Explorer.
    """
    del meta  # retained for call-site compatibility
    return _project_component_roots(request)


def _hdj_text_under_root(path: Path, root: Path) -> str | None:
    """Read ``*.hdj`` only when the resolved target stays under ``root`` (#275)."""
    try:
        resolved = path.resolve()
        resolved.relative_to(root)
    except (OSError, ValueError):
        return None
    if not resolved.is_file():
        return None
    try:
        return resolved.read_text(encoding="utf-8")
    except OSError:
        return None


def _safe_read_text(
    path_str: str | None, meta: object, request: Request | None = None
) -> str | None:
    """Read a file only when it resolves under an allowlisted component root."""
    if not path_str:
        return None
    try:
        candidate = Path(path_str).resolve()
    except OSError:
        return None
    if not candidate.is_file():
        return None
    for root in _allowed_roots(meta, request):
        try:
            candidate.relative_to(root)
        except ValueError:
            continue
        try:
            return candidate.read_text(encoding="utf-8")
        except OSError:
            return None
    return None


def _preview_frame(html: str) -> str:
    """Embed untrusted preview markup in a sandboxed iframe (no scripts)."""
    srcdoc = html_lib.escape(html, quote=True)
    return (
        '<iframe class="preview-frame" sandbox="" referrerpolicy="no-referrer" '
        f'srcdoc="{srcdoc}" title="Component preview"></iframe>'
    )


def _prune_explorer_rate(now: float) -> None:
    """Drop expired timestamps and delete idle client keys (#175)."""
    window = 60.0
    idle: list[str] = []
    for key, stamps in list(_RATE.items()):
        kept = [t for t in stamps if now - t < window]
        if not kept:
            idle.append(key)
        else:
            _RATE[key] = kept
    for key in idle:
        _RATE.pop(key, None)


async def explorer_guards(request: Request) -> None:
    """Rate-limit and audit Explorer requests."""
    client = request.client.host if request.client else "unknown"
    now = time.time()
    _prune_explorer_rate(now)
    bucket = list(_RATE.get(client, []))
    if len(bucket) >= 120:
        _RATE[client] = bucket
        _audit("rate_limited", path=str(request.url.path))
        try:
            from hedron_core.audit import SecurityAuditEventType, emit_security_audit

            emit_security_audit(
                SecurityAuditEventType.EXPLORER_DENIED,
                "Explorer rate limit exceeded",
                attributes={"path": str(request.url.path), "client": client},
            )
        except Exception as exc:  # noqa: BLE001
            _logger.debug("Security audit emit skipped during rate limit: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Explorer rate limit exceeded",
        )
    bucket.append(now)
    _RATE[client] = bucket
    _audit("request", path=str(request.url.path))


def _mount_path(request: Request) -> str:
    """Return the operator-configured or ASGI mount path for Explorer links."""
    from hedron_core.mount import normalize_mount_path

    configured = getattr(request.app.state, "hedron_mount_path", None)
    if isinstance(configured, str) and configured:
        return normalize_mount_path(configured)
    return normalize_mount_path(str(request.scope.get("root_path") or ""))


def _explorer_href(request: Request, path: str) -> str:
    """Build an escaped, mount-aware local Explorer/static URL."""
    normalized_path = "/" + path.lstrip("/")
    mount = _mount_path(request)
    href = f"{mount}{normalized_path}" if mount else normalized_path
    return html_lib.escape(href, quote=True)


def _nav_link(request: Request, key: str, label: str, href: str, active: str) -> str:
    """Render one escaped, mount-aware Explorer navigation link."""
    css_class = "active" if key == active else ""
    return (
        f'<a href="{_explorer_href(request, href)}" class="{css_class}">'
        f"{html_lib.escape(label)}</a>"
    )


def _component_href(request: Request, name: str) -> str:
    """Return an escaped, mount-aware detail URL for a registry component."""
    path = "/hedron-explorer/component/" + name
    return _explorer_href(request, path)


def _shell(title: str, body: str, *, request: Request, active: str = "components") -> str:
    nav = [
        ("components", "Components", "/hedron-explorer/"),
        ("routes", "Routes", "/hedron-explorer/routes"),
        ("graph", "Graph", "/hedron-explorer/graph"),
        ("security", "Security", "/hedron-explorer/security"),
        ("a11y", "Accessibility", "/hedron-explorer/a11y"),
        ("cache", "Cache", "/hedron-explorer/cache"),
        ("data", "Data", "/hedron-explorer/data"),
        ("charts", "Charts", "/hedron-explorer/charts"),
        ("maps", "Maps", "/hedron-explorer/maps"),
        ("extensions", "HTMX extensions", "/hedron-explorer/extensions"),
        ("auto", "Auto", "/hedron-explorer/auto"),
        ("packages", "Packages", "/hedron-explorer/packages"),
        ("elements", "Elements", "/hedron-explorer/elements"),
        ("inventory", "Inventory", "/hedron-explorer/inventory"),
        ("interactions", "Interactions", "/hedron-explorer/interactions"),
        ("features", "Features", "/hedron-explorer/features"),
        ("settings", "Settings", "/hedron-explorer/settings"),
    ]
    links = "".join(_nav_link(request, key, label, href, active) for key, label, href in nav)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html_lib.escape(title)} · Hedron Explorer</title>
  <link rel="stylesheet" href="{_explorer_href(request, "/hedron-explorer/static/explorer.css")}">
  <script src="{_explorer_href(request, "/hedron-static/htmx.min.js")}" defer></script>
  <script src="{_explorer_href(request, "/hedron-static/ext/head-support.js")}" defer></script>
  <script src="{_explorer_href(request, "/hedron-static/ext/sse.js")}" defer></script>
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header>
    <h1>Hedron Explorer</h1>
    <nav aria-label="Explorer">{links}</nav>
  </header>
  <main id="main" tabindex="-1">{body}</main>
</body>
</html>"""


def _find_component(name: str) -> ComponentMeta | None:
    """Resolve a registered component by short name or logical-id suffix."""
    for component in get_registry().components():
        if component.name == name or component.logical_id.endswith(f".{name}"):
            return component
    return None


def _component_detail_body(meta: ComponentMeta, request: Request) -> str:
    """Build the HTML body for a single Explorer component detail page."""
    styles = _safe_read_text(meta.styles_path, meta, request)
    styles_block = (
        html_lib.escape(styles)
        if styles is not None
        else (
            "(styles unavailable or outside allowlisted component roots)"
            if meta.styles_path
            else "(no styles.css)"
        )
    )
    explanations = [
        f"Style symbols: {dict(meta.style_symbols) or '{}'}",
        "Jinja templates are application-level sources managed by hedron-jinja.",
        "Browser modules register as fingerprinted assets when present.",
        "Override style symbols via component STYLE_COMPONENT_ID / local eject.",
    ]
    preview_html = ""
    try:
        from hedron_core import Text

        result = render(Text(f"Preview of {meta.name}"), mode=RenderMode.FRAGMENT)
        preview_html = result.html
        _TRACE.appendleft({"kind": "render", "component": meta.logical_id, "mode": "fragment"})
    except Exception as exc:  # noqa: BLE001
        preview_html = html_lib.escape(str(exc))
    return f"""
        <h2>{html_lib.escape(meta.name)}</h2>
        <p><code>{html_lib.escape(meta.logical_id)}</code></p>
        <section>
          <h3>Preview</h3>
          <div class="preview">{_preview_frame(preview_html)}</div>
        </section>
        <section>
          <h3>Inference explanations</h3>
          <ul>{"".join(f"<li>{html_lib.escape(x)}</li>" for x in explanations)}</ul>
        </section>
        <section>
          <h3>Styles</h3>
          <pre>{styles_block}</pre>
        </section>
        <section>
          <h3>Assets</h3>
          <p>Roots: {html_lib.escape(str([_redact(r) for r in meta.asset_roots]))}</p>
          <p>Browser modules: {html_lib.escape(str([_redact(m) for m in meta.browser_modules]))}</p>
        </section>
        """


def explorer_router() -> APIRouter:
    router = APIRouter(tags=["hedron-explorer"], dependencies=[Depends(explorer_guards)])
    static_dir = Path(__file__).resolve().parent / "static"

    @router.get("/static/{asset_path:path}", include_in_schema=False)
    async def explorer_static(asset_path: str) -> FileResponse:
        if not static_dir.is_dir():
            raise HTTPException(status_code=404, detail="Explorer static assets missing")
        base = static_dir.resolve()
        target = (base / asset_path).resolve()
        try:
            target.relative_to(base)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail="Not found") from exc
        if not target.is_file():
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(target)

    @router.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def index(request: Request) -> str:
        components = list(get_registry().components())
        rows = "".join(
            f"<tr><td><a href='{_component_href(request, c.name)}'>"
            f"{html_lib.escape(c.name)}</a></td>"
            f"<td><code>{html_lib.escape(c.logical_id)}</code></td>"
            f"<td>{html_lib.escape(c.distribution)}</td></tr>"
            for c in components[:200]
        )
        body = f"""
        <h2>Components</h2>
        <table>
          <thead><tr><th>Name</th><th>Logical ID</th><th>Distribution</th></tr></thead>
          <tbody>{rows or "<tr><td colspan='3'>No components</td></tr>"}</tbody>
        </table>
        """
        return _shell("Components", body, request=request, active="components")

    @router.get("/routes", response_class=HTMLResponse, include_in_schema=False)
    async def routes_view(request: Request) -> str:
        routes = list(get_registry().routes())
        rows = "".join(
            f"<tr><td>{html_lib.escape(r.kind)}</td><td>{html_lib.escape(r.name)}</td>"
            f"<td><code>{html_lib.escape(r.path)}</code></td>"
            f"<td>{html_lib.escape(','.join(r.methods))}</td>"
            f"<td><code>{html_lib.escape(str(dict(r.htmx_inference)))}</code></td></tr>"
            for r in routes
        )
        body = f"""
        <h2>Routes</h2>
        <table>
          <thead>
            <tr><th>Kind</th><th>Name</th><th>Path</th><th>Methods</th><th>HTMX</th></tr>
          </thead>
          <tbody>{rows or "<tr><td colspan='5'>No routes</td></tr>"}</tbody>
        </table>
        """
        return _shell("Routes", body, request=request, active="routes")

    @router.get("/component/{name}", response_class=HTMLResponse, include_in_schema=False)
    async def component_detail(name: str, request: Request) -> str:
        meta = _find_component(name)
        if meta is None:
            raise HTTPException(status_code=404, detail=f"Unknown component {name}")
        return _shell(
            meta.name, _component_detail_body(meta, request), request=request, active="components"
        )

    @router.get("/graph", response_class=HTMLResponse, include_in_schema=False)
    async def graph_view(request: Request) -> str:
        edges = []
        for c in get_registry().components():
            if c.styles_path:
                edges.append(f"{c.name} → CSS")
            for m in c.browser_modules:
                edges.append(f"{c.name} → {_redact(m)}")
        items = "".join(f"<li>{html_lib.escape(e)}</li>" for e in edges)
        return _shell(
            "Graph",
            (
                f"<h2>Component graph</h2><ul>{items or '<li>No edges</li>'}</ul>"
                f"<h2>View / command graph</h2>{_handle_graph_html(request)}"
            ),
            request=request,
            active="graph",
        )

    @router.get("/security", response_class=HTMLResponse, include_in_schema=False)
    async def security_view(request: Request) -> str:
        findings = [
            "Explorer absent in production by default",
            "CSRF required for unsafe cookie-authenticated actions",
            "Authenticated fragments use private, no-store caching",
            "Mutation simulation disabled by default",
        ]
        items = "".join(f"<li>{html_lib.escape(f)}</li>" for f in findings)
        return _shell(
            "Security",
            f"<h2>Security findings</h2><ul>{items}</ul>",
            request=request,
            active="security",
        )

    @router.get("/a11y", response_class=HTMLResponse, include_in_schema=False)
    async def a11y_view(request: Request) -> str:
        from hedron_core import Main, Page, Text, render
        from hedron_core.a11y import (
            ACCESSIBILITY_PROFILE,
            AccessibilityContractCatalog,
            AccessibilityScenario,
            seed_reviewed_contracts,
            validate_page_structure,
        )
        from hedron_core.html import html as h
        from hedron_core.security import SafeUrl, UrlPurpose

        catalog = AccessibilityContractCatalog()
        seed_reviewed_contracts(catalog)
        catalog.ensure_registry()
        all_contracts = list(catalog.contracts.values())
        reviewed_count = sum(1 for c in all_contracts if c.reviewed)
        total = len(all_contracts)
        # Prefer reviewed contracts first, then stubs.
        ordered = sorted(all_contracts, key=lambda c: (not c.reviewed, c.component))
        shown = ordered[:40]
        rows = "".join(
            "<tr>"
            f"<td>{html_lib.escape(c.component)}</td>"
            f"<td>{'yes' if c.reviewed else 'stub'}</td>"
            f"<td>{html_lib.escape(c.native_semantics or '—')}</td>"
            f"<td>{html_lib.escape(c.keyboard or '—')}</td>"
            f"<td>{html_lib.escape(c.notes or '—')}</td>"
            "</tr>"
            for c in shown
        )
        sample = render(
            Page(
                h.a(
                    "Skip to content",
                    href=SafeUrl.parse("#main", purpose=UrlPurpose.NAVIGATION),
                ),
                Main(h.h1("Explorer sample"), Text("outline"), id="main"),
                title="Explorer a11y sample",
                lang="en",
            )
        ).html
        structure = validate_page_structure(sample)
        landmark_items = (
            "".join(
                f"<li><code>{html_lib.escape(name)}</code></li>" for name in structure.landmarks
            )
            or "<li>(none)</li>"
        )
        heading_items = (
            "".join(f"<li><code>{html_lib.escape(name)}</code></li>" for name in structure.headings)
            or "<li>(none)</li>"
        )
        profile = ACCESSIBILITY_PROFILE.as_dict()
        scenario = AccessibilityScenario(
            name="explorer-review",
            covers=("keyboard", "focus", "announcements"),
        )
        summary = scenario.summarize()
        modes = [
            "contrast / non-text contrast",
            "target spacing",
            "focus obstruction",
            "text spacing",
            "zoom / reflow / orientation",
            "reduced motion",
            "forced colors",
            "media alternatives",
            "visualization fallbacks",
        ]
        mode_items = "".join(f"<li>{html_lib.escape(m)}</li>" for m in modes)
        body = f"""
        <h2>Accessibility review workspace</h2>
        <p>Findings distinguish automatic, semi-automatic, and manual status.
        Empty scans never summarize as accessible
        (status: <code>{html_lib.escape(str(summary["status"]))}</code>).</p>
        <section aria-labelledby="a11y-profile">
          <h3 id="a11y-profile">Standards profile</h3>
          <dl>
            <dt>Profile</dt><dd><code>{html_lib.escape(str(profile["profile_id"]))}</code></dd>
            <dt>WCAG</dt><dd>{html_lib.escape(str(profile["wcag_version"]))}
              {"/".join(str(level) for level in cast(list[object], profile["wcag_levels"]))}</dd>
            <dt>WAI-ARIA</dt><dd>{html_lib.escape(str(profile["wai_aria_version"]))}</dd>
          </dl>
        </section>
        <section aria-labelledby="a11y-tree">
          <h3 id="a11y-tree">Structure outline</h3>
          <p>Headings and landmarks from a sample Page render
          (<code>validate_page_structure</code>). Browser accessibility trees and
          live-region logs remain review-mode checklists / Playwright evidence,
          not a live AT tree in Explorer.</p>
          <h4>Landmarks</h4>
          <ul>{landmark_items}</ul>
          <h4>Headings</h4>
          <ul>{heading_items}</ul>
          <h4>Review modes</h4>
          <ul>{mode_items}</ul>
        </section>
        <section aria-labelledby="a11y-contracts">
          <h3 id="a11y-contracts">Component contracts</h3>
          <p>Showing {len(shown)} of {total} contracts
          ({reviewed_count} reviewed; curated REQUIRED set plus registry stubs).</p>
          <table>
            <thead><tr><th>Component</th><th>Reviewed</th><th>Semantics</th>
            <th>Keyboard</th><th>Notes</th></tr></thead>
            <tbody>{rows or "<tr><td colspan='5'>No contracts</td></tr>"}</tbody>
          </table>
        </section>
        <section aria-labelledby="a11y-atag">
          <h3 id="a11y-atag">ATAG authoring assistance</h3>
          <p>Accessibility properties are listed alongside ordinary props on component pages.
          Repair guidance is reversible and author-reviewed; features default on.</p>
        </section>
        """
        return _shell("Accessibility", body, request=request, active="a11y")

    @router.get("/cache", response_class=HTMLResponse, include_in_schema=False)
    async def cache_view(request: Request) -> str:
        from hedron_core.cache import CacheTrace

        events = CacheTrace.recent(50)
        rows = "".join(
            "<tr>"
            f"<td>{html_lib.escape(str(e['kind']))}</td>"
            f"<td><code>{html_lib.escape(str(e['key_fingerprint']))}</code></td>"
            f"<td>{html_lib.escape(str(e['scope']))}</td>"
            f"<td>{html_lib.escape(str(e.get('age_ms')))}</td>"
            f"<td>{html_lib.escape(str(e.get('size')))}</td>"
            f"<td>{html_lib.escape(str(e.get('detail') or ''))}</td>"
            "</tr>"
            for e in events
        )
        body = f"""
        <h2>Cache traces</h2>
        <p>Key fingerprints only — secret values are never shown.</p>
        <table>
          <thead><tr><th>Kind</th><th>Key</th><th>Scope</th><th>Age ms</th>
          <th>Size</th><th>Detail</th></tr></thead>
          <tbody>{rows or "<tr><td colspan='6'>No cache activity</td></tr>"}</tbody>
        </table>
        """
        return _shell("Cache", body, request=request, active="cache")

    @router.get("/charts", response_class=HTMLResponse, include_in_schema=False)
    async def charts_view(request: Request) -> str:
        from hedron_core.registry import get_registry

        registry = get_registry()
        chart_components = [
            c
            for c in registry.components()
            if c.distribution == "hedron-charts"
            or c.name in {"LineChart", "MatplotlibChart", "PlotlyChart", "AltairChart"}
        ]
        rows = "".join(
            "<tr>"
            f"<td><code>{html_lib.escape(c.name)}</code></td>"
            f"<td><code>{html_lib.escape(c.distribution)}</code></td>"
            f"<td>{html_lib.escape(c.accessibility_notes or '')}</td>"
            f"<td>{'yes' if c.browser_modules else 'no'}</td>"
            "</tr>"
            for c in chart_components
        )
        assets = "".join(
            f"<li><code>{html_lib.escape(a.logical_id)}</code> ({html_lib.escape(a.kind)})</li>"
            for a in registry.assets()
            if "chart" in a.logical_id or "plotly" in a.logical_id or "vega" in a.logical_id
        )
        body = f"""
        <h2>Visualization</h2>
        <p>Charts require title and description/alt/waiver. Payload limits and secret
        redaction are enforced by adapters. Browser runtimes are pinned and local.</p>
        <h3>Registered chart components</h3>
        <table>
          <thead><tr><th>Name</th><th>Distribution</th><th>A11y notes</th>
          <th>Browser host</th></tr></thead>
          <tbody>{rows or "<tr><td colspan='4'>No chart components registered</td></tr>"}</tbody>
        </table>
        <h3>Chart assets</h3>
        <ul>{assets or "<li>No chart assets registered yet</li>"}</ul>
        <h3>Security policy</h3>
        <ul>
          <li>Reject raw JavaScript callbacks</li>
          <li>Reject unapproved remote CDN URLs</li>
          <li>Private authenticated caching defaults apply</li>
        </ul>
        """
        return _shell("Charts", body, request=request, active="charts")

    @router.get("/maps", response_class=HTMLResponse, include_in_schema=False)
    async def maps_view(request: Request) -> str:
        from hedron_core.registry import get_registry

        registry = get_registry()
        map_components = [
            c
            for c in registry.components()
            if c.distribution == "hedron-maps"
            or c.name == "Map"
            and "hedron_maps" in (c.module or "")
        ]
        rows = "".join(
            "<tr>"
            f"<td><code>{html_lib.escape(c.name)}</code></td>"
            f"<td><code>{html_lib.escape(c.distribution)}</code></td>"
            f"<td>{html_lib.escape(c.accessibility_notes or '')}</td>"
            "</tr>"
            for c in map_components
        )
        assets = "".join(
            f"<li><code>{html_lib.escape(a.logical_id)}</code> ({html_lib.escape(a.kind)})</li>"
            for a in registry.assets()
            if "hedron-maps" in a.logical_id or "maplibre" in a.logical_id
        )
        body = f"""
        <h2>Maps</h2>
        <p>Explorer inspects compiled MapPlan facts, origins, attribution, CSP, fallback,
        and event schemas without executing untrusted map data.</p>
        <h3>Registered map components</h3>
        <table>
          <thead><tr><th>Name</th><th>Distribution</th><th>A11y notes</th></tr></thead>
          <tbody>{rows or "<tr><td colspan='3'>No map components registered</td></tr>"}</tbody>
        </table>
        <h3>Map assets</h3>
        <ul>{assets or "<li>No map assets registered yet</li>"}</ul>
        <h3>Closed events</h3>
        <ul>
          <li>feature-selected / feature-activated</li>
          <li>viewport-changed (map.viewport)</li>
          <li>layer-visibility-changed</li>
          <li>map-loaded / map-failed</li>
        </ul>
        """
        return _shell("Maps", body, request=request, active="maps")

    @router.get("/extensions", response_class=HTMLResponse, include_in_schema=False)
    async def extensions_view(request: Request) -> str:
        from hedron_core.htmx_extensions import catalog_facts

        facts = catalog_facts()
        rows = "".join(
            "<tr>"
            f"<td><code>{html_lib.escape(str(item.get('public_id', '')))}</code></td>"
            f"<td><code>{html_lib.escape(str(item.get('asset_name', '')))}</code></td>"
            f"<td>{html_lib.escape(str(item.get('version', '')))}</td>"
            f"<td><code>{html_lib.escape(str(item.get('hdj_extension_id', '')))}</code></td>"
            "</tr>"
            for item in facts["extensions"]
        )
        body = f"""
        <h2>HTMX extensions</h2>
        <p>Explorer lists catalog facts without executing untrusted extension code.
        Writing <code>hx-ext</code> never installs an asset. Morph is not admitted
        on this train.</p>
        <p>new_catalog_kind={facts.get("new_catalog_kind")} ·
        feature_bundle_executor={facts.get("feature_bundle_executor")} ·
        morph_admitted={facts.get("morph_admitted")}</p>
        <table>
          <thead>
            <tr><th>Public id</th><th>Asset name</th><th>Version</th><th>HDJ id</th></tr>
          </thead>
          <tbody>{rows or "<tr><td colspan='4'>No catalog facts</td></tr>"}</tbody>
        </table>
        """
        return _shell("HTMX extensions", body, request=request, active="extensions")

    @router.get("/data", response_class=HTMLResponse, include_in_schema=False)
    async def data_view(request: Request) -> str:
        from hedron_core.registry import get_registry

        registry = get_registry()
        data_components = [
            c
            for c in registry.components()
            if c.name in {"DataTable", "DataEditor"} or "hedron_data" in (c.module or "")
        ]
        rows = "".join(
            "<tr>"
            f"<td><code>{html_lib.escape(c.name)}</code></td>"
            f"<td><code>{html_lib.escape(c.distribution)}</code></td>"
            f"<td>{html_lib.escape(c.accessibility_notes or '')}</td>"
            f"<td>{'yes' if c.browser_modules else 'no'}</td>"
            "</tr>"
            for c in data_components
        )
        sample_schema = (
            "<tr><td>id</td><td>read-only key</td><td>no</td></tr>"
            "<tr><td>name</td><td>text</td><td>yes</td></tr>"
            "<tr><td>title</td><td>text</td><td>yes</td></tr>"
            "<tr><td>active</td><td>boolean</td><td>yes</td></tr>"
        )
        body = f"""
        <h2>Data</h2>
        <p>Explorer data previews use isolated sample rows by default.
        Writable-field policy is server-authoritative; forged writes are rejected.</p>
        <h3>Registered data components</h3>
        <table>
          <thead><tr><th>Name</th><th>Distribution</th><th>A11y notes</th>
          <th>Browser host</th></tr></thead>
          <tbody>{
            rows or "<tr><td colspan='4'>No DataTable/DataEditor registered</td></tr>"
        }</tbody>
        </table>
        <h3>Sample writable policy</h3>
        <table>
          <thead><tr><th>Field</th><th>Role</th><th>Writable</th></tr></thead>
          <tbody>{sample_schema}</tbody>
        </table>
        <ul>
          <li>Schema and column editors derive from Hedron Field metadata</li>
          <li>Changes, conflicts, timing, and endpoints appear on save diagnostics</li>
          <li>Large sources must use bounded DataEditorSource paging</li>
        </ul>
        """
        return _shell("Data", body, request=request, active="data")

    @router.get("/auto", response_class=HTMLResponse, include_in_schema=False)
    async def auto_view(request: Request) -> str:
        from hedron_core.auto import get_last_auto_decision

        decision = get_last_auto_decision()
        if decision is None:
            detail = "<p>No Auto() decision recorded yet in this process.</p>"
        else:
            rejected = "".join(
                f"<li><code>{html_lib.escape(name)}</code>: {html_lib.escape(reason)}</li>"
                for name, reason in decision.rejected
            )
            detail = f"""
            <dl>
              <dt>Selected</dt>
              <dd><code>{html_lib.escape(decision.selected)}</code></dd>
              <dt>Candidates</dt>
              <dd><code>{html_lib.escape(", ".join(decision.candidates))}</code></dd>
              <dt>Inspection</dt>
              <dd><pre>{html_lib.escape(str(dict(decision.inspection)))}</pre></dd>
            </dl>
            <h3>Rejected</h3>
            <ul>{rejected or "<li>None</li>"}</ul>
            """
        body = f"<h2>Auto renderer evidence</h2>{detail}"
        return _shell("Auto", body, request=request, active="auto")

    @router.get("/packages", response_class=HTMLResponse, include_in_schema=False)
    async def packages_view(request: Request) -> str:
        panels = get_explorer_panels()
        items = "".join(
            f"<li><strong>{html_lib.escape(p.title)}</strong> "
            f"({html_lib.escape(p.plugin)}): {html_lib.escape(p.description)}</li>"
            for p in panels
        )
        return _shell(
            "Packages",
            f"<h2>Packages / plugin panels</h2><ul>{items or '<li>No plugin panels</li>'}</ul>",
            request=request,
            active="packages",
        )

    @router.get("/elements", response_class=HTMLResponse, include_in_schema=False)
    async def elements_view(request: Request) -> str:
        rows = []
        for meta in get_registry().element_definitions():
            href = _explorer_href(request, f"/hedron-explorer/elements/{meta.logical_id}")
            events = html_lib.escape(", ".join(meta.events) or "—")
            parts = html_lib.escape(", ".join(meta.parts) or "—")
            origin = "first-party" if meta.first_party else "third-party"
            rows.append(
                "<tr>"
                f'<td><a href="{href}">{html_lib.escape(meta.logical_id)}</a></td>'
                f"<td>{html_lib.escape(meta.tag_name)}</td>"
                f"<td>{meta.abi_version}</td>"
                f"<td>{origin}</td>"
                f"<td>{events}</td>"
                f"<td>{parts}</td>"
                "</tr>"
            )
        empty = '<tr><td colspan="6">No element definitions</td></tr>'
        body = (
            "<h2>Elements</h2>"
            "<table><thead><tr>"
            "<th>Logical id</th><th>Tag</th><th>ABI</th><th>Origin</th>"
            "<th>Events</th><th>Parts</th></tr></thead>"
            f"<tbody>{''.join(rows) or empty}</tbody></table>"
        )
        return _shell("Elements", body, request=request, active="elements")

    @router.get("/elements/{logical_id:path}", response_class=HTMLResponse, include_in_schema=False)
    async def element_detail_view(request: Request, logical_id: str) -> str:
        meta = get_registry().get_element_definition(logical_id)
        if meta is None:
            raise HTTPException(status_code=404, detail="Element not found")
        fallback = "".join(
            f"<li><code>{html_lib.escape(key)}</code>: {html_lib.escape(value)}</li>"
            for key, value in meta.fallback.items()
        )
        body = f"""
        <h2>{html_lib.escape(meta.tag_name)}</h2>
        <dl>
          <dt>Logical id</dt><dd>{html_lib.escape(meta.logical_id)}</dd>
          <dt>ABI</dt><dd>{meta.abi_version}</dd>
          <dt>Module</dt><dd>{html_lib.escape(meta.module_asset_id)}</dd>
          <dt>Events</dt><dd>{html_lib.escape(", ".join(meta.events) or "—")}</dd>
          <dt>Parts</dt><dd>{html_lib.escape(", ".join(meta.parts) or "—")}</dd>
          <dt>Slots</dt><dd>{html_lib.escape(", ".join(meta.slots) or "—")}</dd>
          <dt>Tokens</dt><dd>{html_lib.escape(", ".join(meta.tokens) or "—")}</dd>
          <dt>First party</dt><dd>{meta.first_party}</dd>
        </dl>
        <h3>Fallback</h3>
        <ul>{fallback or "<li>None declared</li>"}</ul>
        """
        return _shell(meta.tag_name, body, request=request, active="elements")

    @router.post("/api/element-simulate", include_in_schema=False)
    async def api_element_simulate(request: Request) -> Any:
        try:
            payload = await request.json()
        except Exception:  # noqa: BLE001
            return JSONResponse({"detail": "Invalid JSON body"}, status_code=400)
        if not isinstance(payload, dict):
            return JSONResponse({"detail": "JSON object required"}, status_code=400)
        logical_id = payload.get("logical_id")
        failure = payload.get("failure", "none")
        if not isinstance(logical_id, str) or not logical_id:
            return JSONResponse({"detail": "logical_id required"}, status_code=400)
        if failure not in {"none", "module", "upgrade"}:
            return JSONResponse({"detail": "failure must be none|module|upgrade"}, status_code=400)
        meta = get_registry().get_element_definition(logical_id)
        if meta is None:
            return JSONResponse({"detail": "Element not found"}, status_code=404)
        behavior = {
            "none": meta.fallback.get("pre_upgrade", "server content visible"),
            "module": meta.fallback.get("module_failure", "retain server content"),
            "upgrade": meta.fallback.get("js_off", "server content visible"),
        }[failure]
        return {
            "logical_id": meta.logical_id,
            "tag_name": meta.tag_name,
            "failure": failure,
            "fallback": behavior,
            "declared_fallback": dict(meta.fallback),
        }

    @router.get("/inventory", response_class=HTMLResponse, include_in_schema=False)
    async def inventory_view(request: Request) -> str:
        """Production / HDJ inventory panel (phase 0.11)."""
        try:
            from hedron_jinja import build_production_inventory, reconcile_csp
            from hedron_jinja.source import inferred_capabilities, parse_hdj_source

            reports: list[JsonObject] = []
            caps: set[str] = set()
            mismatches: list[str] = []
            project_root = getattr(request.app.state, "hedron_project_root", None)
            roots = _project_component_roots(request)
            search_roots = list(roots)
            if project_root:
                search_roots.append(Path(project_root))
            seen: set[Path] = set()
            for root in search_roots:
                root = Path(root).resolve()
                if root in seen or not root.exists():
                    continue
                seen.add(root)
                for path in sorted(root.rglob("*.hdj")):
                    if any(part.startswith(".") for part in path.parts):
                        continue
                    source = _hdj_text_under_root(path, root)
                    if source is None:
                        continue
                    try:
                        rel = str(path.relative_to(root))
                        parsed = parse_hdj_source(rel, source)
                        required = sorted(
                            set(inferred_capabilities(parsed)) | set(parsed.declaration.requires)
                        )
                        caps.update(required)
                        reports.append(
                            cast(
                                JsonObject,
                                {
                                    "name": rel,
                                    "kind": str(parsed.declaration.kind),
                                    "capabilities": required,
                                },
                            )
                        )
                        mismatches.extend(
                            reconcile_csp(
                                None,
                                required_capabilities=required,
                                source_name=rel,
                            )
                        )
                    except Exception as exc:  # noqa: BLE001
                        reports.append({"name": str(path), "error": str(exc)})
            inv = build_production_inventory(
                template_reports=reports,
                capabilities=sorted(caps) or ("web.html", "jinja.core"),
            )
            payload = html_lib.escape(
                str(
                    {
                        **inv.as_dict(),
                        "csp_mismatches": mismatches,
                        "template_count": len(reports),
                    }
                )
            )
        except Exception as exc:  # noqa: BLE001
            payload = html_lib.escape(f"Inventory unavailable: {exc}")
        body = f"<h2>Production inventory</h2><pre>{payload}</pre>"
        return _shell("Inventory", body, request=request, active="inventory")

    @router.get("/settings", response_class=HTMLResponse, include_in_schema=False)
    async def settings_view(request: Request) -> str:
        theme = getattr(request.app.state, "hedron_theme", None)
        production = getattr(request.app.state, "hedron_production", None)
        body = f"""
        <h2>Settings</h2>
        <dl>
          <dt>Theme</dt><dd>{html_lib.escape(str(theme))}</dd>
          <dt>Production</dt><dd>{html_lib.escape(str(production))}</dd>
          <dt>Allow mutations</dt><dd>false (default)</dd>
        </dl>
        """
        return _shell("Settings", body, request=request, active="settings")

    @router.get("/interactions", response_class=HTMLResponse, include_in_schema=False)
    async def interactions_view(request: Request) -> str:
        catalog = _app_catalog(request.app)
        rows = []
        for entry in catalog.entries.values():
            ident = html_lib.escape(entry.logical_id)
            kind = html_lib.escape(entry.kind)
            effect = html_lib.escape(entry.effect_state)
            desc = html_lib.escape(entry.descriptor_fingerprint)
            schema = html_lib.escape(entry.type_schema_fingerprint or "absent")
            namespaces = html_lib.escape(", ".join(sorted(entry.projections)) or "none")
            rows.append(
                f"<tr><td>{ident}</td><td>{kind}</td><td>{effect}</td>"
                f"<td><code>{desc}</code></td><td><code>{schema}</code></td>"
                f"<td>{namespaces}</td></tr>"
            )
        projections = "".join(
            f"<li><code>{html_lib.escape(name)}</code> "
            f"provider={html_lib.escape(item.provider)}</li>"
            for name, item in catalog.catalog_projections.items()
        )
        body = f"""
        <h2>Interaction catalog</h2>
        <p>Read-only index of 0.43 descriptors and optional 0.44 TypeSchema.
        Catalog ids and fingerprints are not capabilities.</p>
        <p>Fingerprint <code>{html_lib.escape(catalog.fingerprint)}</code>
        sealed={catalog.sealed}</p>
        <h3>Entries</h3>
        <table>
          <thead><tr><th>Logical id</th><th>Kind</th><th>Effect</th>
          <th>Descriptor</th><th>TypeSchema</th><th>Projections</th></tr></thead>
          <tbody>{"".join(rows) or "<tr><td colspan='6'>No registered handles</td></tr>"}</tbody>
        </table>
        <h3>Package projections</h3>
        <ul>{projections or "<li>No catalog-level projections</li>"}</ul>
        <h3>Provenance</h3>
        <pre>{html_lib.escape(str(dict(catalog.provenance)))}</pre>
        """
        return _shell("Interactions", body, request=request, active="interactions")

    @router.get("/features", response_class=HTMLResponse, include_in_schema=False)
    async def features_view(request: Request) -> str:
        from hedron_core.bundles import included_bundles

        app_id = str(getattr(getattr(request.app, "state", None), "hedron_app_id", "") or "")
        rows = []
        for bundle in included_bundles(app_id=app_id or None):
            ident = html_lib.escape(bundle.logical_id)
            provider = html_lib.escape(f"{bundle.provider} {bundle.provider_version}")
            views = html_lib.escape(
                ", ".join(str(getattr(item, "logical_id", item)) for item in bundle.views) or "—"
            )
            commands = html_lib.escape(
                ", ".join(str(getattr(item, "logical_id", item)) for item in bundle.commands) or "—"
            )
            projections = html_lib.escape(
                ", ".join(item.namespace for item in bundle.projections) or "—"
            )
            limitations = html_lib.escape("; ".join(bundle.limitations) or "—")
            rows.append(
                f"<tr><td>{ident}</td><td>{provider}</td><td>{views}</td>"
                f"<td>{commands}</td><td>{projections}</td><td>{limitations}</td></tr>"
            )
        empty = '<tr><td colspan="6">No FeatureBundles included</td></tr>'
        body = f"""
        <h2>Feature bundles</h2>
        <p>Opt-in package features compiled to ordinary handles. Bundles are not executors
        and catalog/projection presence is not a capability.</p>
        <table>
          <thead><tr><th>Id</th><th>Provider</th><th>Views</th><th>Commands</th>
          <th>Projections</th><th>Limitations</th></tr></thead>
          <tbody>{"".join(rows) or empty}</tbody>
        </table>
        """
        return _shell("Features", body, request=request, active="features")

    @router.get("/api/routes", include_in_schema=False)
    async def api_routes() -> list[dict[str, Any]]:
        return [
            {
                "kind": r.kind,
                "name": r.name,
                "path": r.path,
                "methods": list(r.methods),
                "operation_id": r.operation_id,
                "htmx_inference": dict(r.htmx_inference),
                "explanations": [
                    f"HX target inference: {dict(r.htmx_inference)}",
                    "Override via explicit hx-* attributes on the component.",
                ],
            }
            for r in get_registry().routes()
        ]

    @router.get("/api/security", include_in_schema=False)
    async def api_security() -> dict[str, Any]:
        return {
            "findings": [
                "Explorer routes absent in production by default",
                "CSRF required for unsafe cookie-authenticated actions",
                "Authenticated fragments use private, no-store caching",
                "Mutation simulation disabled by default",
            ],
            "redacted": True,
            "audit_tail": list(_AUDIT)[:20],
        }

    @router.get("/api/components", include_in_schema=False)
    async def api_components() -> list[dict[str, Any]]:
        return [
            {
                "name": c.name,
                "logical_id": c.logical_id,
                "distribution": c.distribution,
                "styles_path": _redact(c.styles_path),
                "style_symbols": dict(c.style_symbols),
            }
            for c in get_registry().components()
        ]

    @router.get("/api/graph", include_in_schema=False)
    async def api_graph() -> dict[str, Any]:
        nodes = [{"id": c.logical_id, "name": c.name} for c in get_registry().components()]
        edges = []
        for c in get_registry().components():
            if c.styles_path:
                edges.append(
                    {
                        "from": c.logical_id,
                        "to": _redact(c.styles_path),
                        "kind": "styles",
                    }
                )
        return {"nodes": nodes, "edges": edges}

    @router.get("/api/handle-graph", include_in_schema=False)
    async def api_handle_graph(request: Request) -> dict[str, Any]:
        """View-command-output graph (not the asset graph or 0.17 InteractionGraph)."""
        from hedron_core.updates import handle_graph_payload, redacted_descriptor_view

        app_id = str(getattr(getattr(request.app, "state", None), "hedron_app_id", "") or "")
        payload = handle_graph_payload(app_id=app_id or None)
        handles = getattr(getattr(request.app, "state", None), "hedron_handles", {}) or {}
        redacted = []
        for handle in handles.values() if isinstance(handles, dict) else []:
            descriptor = getattr(handle, "descriptor", None)
            if descriptor is not None:
                redacted.append(redacted_descriptor_view(descriptor))
        return {**payload, "handles": redacted}

    @router.get("/api/interactions", include_in_schema=False)
    async def api_interactions(request: Request) -> dict[str, Any]:
        catalog = _app_catalog(request.app)
        return catalog.to_manifest(profile="development").as_mapping()

    @router.get("/api/dashboard-graph", include_in_schema=False)
    async def api_dashboard_graph() -> dict[str, Any]:
        """Experimental InteractionGraph JSON shape for Explorer overlays."""
        from hedron_core import InteractionGraph

        payload = dashboard_graph_payload(InteractionGraph())
        return {**payload, "stability": "experimental"}

    @router.post("/api/simulate", include_in_schema=False)
    async def api_simulate(request: Request) -> Any:
        try:
            payload = await request.json()
        except Exception:  # noqa: BLE001
            return JSONResponse({"detail": "Invalid JSON body"}, status_code=400)
        if not isinstance(payload, dict):
            return JSONResponse({"detail": "JSON object required"}, status_code=400)
        unknown = set(payload) - _SIMULATE_KEYS
        if unknown:
            return JSONResponse(
                {"detail": f"Unknown keys: {', '.join(sorted(unknown))}"},
                status_code=400,
            )
        if payload.get("allow_mutations"):
            return JSONResponse(
                {"detail": "Mutation simulation is disabled by default"},
                status_code=403,
            )

        policy = getattr(request.app.state, "hedron_security", None)
        if policy is None:
            return JSONResponse(
                {"detail": "CSRF policy required for simulate"},
                status_code=403,
            )
        # Simulate always requires CSRF validation (ignore csrf_enabled=False).
        # Deny when no strategy can validate rather than silently skipping.
        from hedron_core.csrf import validate_double_submit

        strategy = None
        resolve = getattr(policy, "resolve_csrf_strategy", None)
        if callable(resolve):
            try:
                strategy = resolve()
            except Exception as exc:  # noqa: BLE001 — surface as CSRF failure
                return JSONResponse(
                    {"detail": f"CSRF strategy resolve failed: {exc}"},
                    status_code=403,
                )
        if strategy is None and getattr(policy, "csrf_enabled", True):
            # Prefer an explicit strategy when CSRF is required; fall through to
            # double-submit only when the policy intentionally has no strategy.
            pass
        csrf_name = (
            getattr(strategy, "cookie_name", None)
            or getattr(policy, "csrf_cookie_name", None)
            or "hedron_csrf"
        )
        cookie = request.cookies.get(csrf_name)
        header_name = (
            getattr(strategy, "header_name", None)
            or getattr(policy, "csrf_header_name", None)
            or "X-CSRF-Token"
        )
        header = (
            request.headers.get(header_name)
            or request.headers.get("X-CSRF-Token")
            or request.headers.get("X-Hedron-CSRF")
        )
        form_token = None
        # Simulate always requires a real CSRF check. When the app has
        # csrf_enabled=False, hedron_csrf_validate is a no-op — force
        # double-submit instead of treating the bridge as success (#156).
        if strategy is None:
            if not validate_double_submit(
                cookie_token=cookie, header_token=header, form_token=form_token
            ):
                return JSONResponse({"detail": "CSRF validation failed"}, status_code=403)
        else:
            validator = getattr(request.app.state, "hedron_csrf_validate", None)
            if callable(validator):
                try:
                    result = validator(request, policy)
                    if hasattr(result, "__await__"):
                        await result  # type: ignore[misc]
                except Exception:  # noqa: BLE001
                    return JSONResponse({"detail": "CSRF validation failed"}, status_code=403)
            elif not validate_double_submit(
                cookie_token=cookie, header_token=header, form_token=form_token
            ):
                return JSONResponse({"detail": "CSRF validation failed"}, status_code=403)

        name = payload.get("route")
        if not isinstance(name, str) or not name:
            return JSONResponse({"detail": "route is required"}, status_code=400)
        routes = {r.name: r for r in get_registry().routes()}
        if name not in routes:
            return JSONResponse(
                {"detail": "Unregistered route identifier"},
                status_code=400,
            )
        _TRACE.appendleft({"kind": "simulate", "route": name, "mutations": False})
        mode = str(payload.get("mode") or "fragment")
        route = routes[name]
        inference = dict(getattr(route, "htmx_inference", {}) or {})
        status_code = int(payload.get("status") or 200)
        target = payload.get("target")
        regions_raw = inference.get("fragment_regions") or ""
        regions: dict[str, str] = {}
        if isinstance(regions_raw, dict):
            regions = {str(k): str(v) for k, v in regions_raw.items()}
        elif isinstance(regions_raw, str) and regions_raw.startswith("{"):
            import ast

            try:
                parsed = ast.literal_eval(regions_raw)
            except (SyntaxError, ValueError):
                parsed = {}
            if isinstance(parsed, dict):
                regions = {str(k): str(v) for k, v in parsed.items()}
        region_ok = True
        region_error = None
        if target and regions:
            region_ok = any(target == value.split("|", 1)[0] for _rid, value in regions.items())
            if not region_ok:
                region_error = f"HX-Target {target!r} is not an authorized fragment region"
        methods = tuple(route.methods or ("GET",))
        method = methods[0]
        swap = str(inference.get("swap") or "outerHTML")
        csrf_required = inference.get("csrf_required")
        if csrf_required is None:
            csrf_required = any(m.upper() not in {"GET", "HEAD", "OPTIONS"} for m in methods)
        else:
            csrf_required = str(csrf_required).lower() in {"1", "true", "yes"}
        declared_regions = [
            {"id": rid, "selector": value.split("|", 1)[0]} for rid, value in regions.items()
        ]
        click_preview = {
            "method": method,
            "path": route.path,
            "target": target,
            "swap": swap,
            "csrf_required": bool(csrf_required),
            "declared_regions": declared_regions,
        }
        return cast(
            JsonObject,
            {
                "ok": region_ok,
                "route": name,
                "mutations": False,
                "mode": mode,
                "boosted": bool(payload.get("boosted")),
                "history_restore": bool(payload.get("history_restore")),
                "status": status_code,
                "target": target,
                "primary": {
                    "kind": route.kind,
                    "path": route.path,
                    "swap": swap,
                },
                "oob": [],
                "event_timing": {"trigger": None, "after_swap": None, "after_settle": None},
                "history": "push" if mode in {"boosted", "page"} else "none",
                "assets": "predeclared-shell",
                "cache_variation": ["HX-Request", "HX-History-Restore-Request"]
                + (["HX-Target"] if inference.get("fragment_regions") else []),
                "inference": inference,
                "override_source": "route.htmx_inference",
                "error": region_error,
                "click_preview": click_preview,
            },
        )

    @router.get("/api/click-preview", include_in_schema=False)
    async def api_click_preview(request: Request) -> Any:
        """Explain method/path/target/swap for a registered route (Explorer preview)."""
        name = request.query_params.get("route")
        target = request.query_params.get("target")
        if not name:
            return JSONResponse({"detail": "route query parameter is required"}, status_code=400)
        routes = {r.name: r for r in get_registry().routes()}
        if name not in routes:
            return JSONResponse({"detail": "Unregistered route identifier"}, status_code=400)
        route = routes[name]
        inference = dict(getattr(route, "htmx_inference", {}) or {})
        regions_raw = inference.get("fragment_regions") or ""
        regions: dict[str, str] = {}
        if isinstance(regions_raw, dict):
            regions = {str(k): str(v) for k, v in regions_raw.items()}
        elif isinstance(regions_raw, str) and regions_raw.startswith("{"):
            import ast

            try:
                parsed = ast.literal_eval(regions_raw)
            except (SyntaxError, ValueError):
                parsed = {}
            if isinstance(parsed, dict):
                regions = {str(k): str(v) for k, v in parsed.items()}
        methods = tuple(route.methods or ("GET",))
        csrf_required = inference.get("csrf_required")
        if csrf_required is None:
            csrf_required = any(m.upper() not in {"GET", "HEAD", "OPTIONS"} for m in methods)
        else:
            csrf_required = str(csrf_required).lower() in {"1", "true", "yes"}
        return cast(
            JsonObject,
            {
                "click_preview": {
                    "method": methods[0],
                    "path": route.path,
                    "target": target,
                    "swap": str(inference.get("swap") or "outerHTML"),
                    "csrf_required": bool(csrf_required),
                    "declared_regions": [
                        {"id": rid, "selector": value.split("|", 1)[0]}
                        for rid, value in regions.items()
                    ],
                }
            },
        )

    return router


def reset_explorer_runtime_for_tests() -> None:
    """Clear rate-limit / audit state between tests."""
    _TRACE.clear()
    _RATE.clear()
    _AUDIT.clear()
