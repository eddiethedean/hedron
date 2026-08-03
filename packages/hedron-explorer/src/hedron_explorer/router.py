"""Component Explorer router with HTMX panels (phase 0.4)."""

from __future__ import annotations

import html as html_lib
import time
from collections import deque
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from hedron_core.plugins import get_explorer_panels
from hedron_core.registry import get_registry
from hedron_core.rendering import RenderMode, render

__all__ = ["explorer_router"]

_TRACE: deque[dict[str, Any]] = deque(maxlen=100)
_RATE: dict[str, list[float]] = {}
_AUDIT: deque[dict[str, Any]] = deque(maxlen=200)
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


def _audit(event: str, **payload: Any) -> None:
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
                roots.extend(settings.resolved_roots(base=Path(project_root)))
            else:
                # Optional: flagship config without hard-depending on `hedron`.
                from importlib import import_module

                mod = import_module("hedron.config")
                settings = mod.load_hedron_settings(Path(project_root))
                roots.extend(settings.resolved_roots(base=Path(project_root)))
        except Exception:  # noqa: BLE001 — explorer stays available without config
            pass
    return roots


def _allowed_roots(meta: Any, request: Request | None = None) -> list[Path]:
    """Allow reads under project component roots only.

    ``meta.folder_path`` is ignored as a root: registry metadata can be
    attacker-influenced when browsing components in Explorer.
    """
    del meta  # retained for call-site compatibility
    return _project_component_roots(request)


def _safe_read_text(path_str: str | None, meta: Any, request: Request | None = None) -> str | None:
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


async def explorer_guards(request: Request) -> None:
    """Rate-limit and audit Explorer requests."""
    client = request.client.host if request.client else "unknown"
    now = time.time()
    bucket = [t for t in _RATE.get(client, []) if now - t < 60]
    if len(bucket) >= 120:
        _RATE[client] = bucket
        _audit("rate_limited", path=str(request.url.path))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Explorer rate limit exceeded",
        )
    bucket.append(now)
    _RATE[client] = bucket
    _audit("request", path=str(request.url.path))


def _shell(title: str, body: str, *, active: str = "components") -> str:
    nav = [
        ("components", "Components", "/hedron-explorer/"),
        ("routes", "Routes", "/hedron-explorer/routes"),
        ("graph", "Graph", "/hedron-explorer/graph"),
        ("security", "Security", "/hedron-explorer/security"),
        ("a11y", "Accessibility", "/hedron-explorer/a11y"),
        ("cache", "Cache", "/hedron-explorer/cache"),
        ("data", "Data", "/hedron-explorer/data"),
        ("charts", "Charts", "/hedron-explorer/charts"),
        ("auto", "Auto", "/hedron-explorer/auto"),
        ("packages", "Packages", "/hedron-explorer/packages"),
        ("settings", "Settings", "/hedron-explorer/settings"),
    ]
    links = "".join(
        f'<a href="{href}" class="{"active" if key == active else ""}">{html_lib.escape(label)}</a>'
        for key, label, href in nav
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html_lib.escape(title)} · Hedron Explorer</title>
  <link rel="stylesheet" href="/hedron-explorer/static/explorer.css">
  <script src="/hedron-static/htmx.min.js" defer></script>
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
    async def index() -> str:
        components = list(get_registry().components())
        rows = "".join(
            f"<tr><td><a href='/hedron-explorer/component/{html_lib.escape(c.name)}'>"
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
        return _shell("Components", body, active="components")

    @router.get("/routes", response_class=HTMLResponse, include_in_schema=False)
    async def routes_view() -> str:
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
        return _shell("Routes", body, active="routes")

    @router.get("/component/{name}", response_class=HTMLResponse, include_in_schema=False)
    async def component_detail(name: str, request: Request) -> str:
        meta = None
        for c in get_registry().components():
            if c.name == name or c.logical_id.endswith(f".{name}"):
                meta = c
                break
        if meta is None:
            raise HTTPException(status_code=404, detail=f"Unknown component {name}")
        hdn = _safe_read_text(meta.hdn_source, meta, request)
        styles = _safe_read_text(meta.styles_path, meta, request)
        hdn_block = (
            html_lib.escape(hdn)
            if hdn is not None
            else (
                "(template unavailable or outside allowlisted component roots)"
                if meta.hdn_source
                else "(no template.hdn)"
            )
        )
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
            "HDN templates compile ahead of time in production (HED-BUILD-0004).",
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
        body = f"""
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
          <h3>Source / HDN</h3>
          <pre>{hdn_block}</pre>
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
        return _shell(meta.name, body, active="components")

    @router.get("/graph", response_class=HTMLResponse, include_in_schema=False)
    async def graph_view() -> str:
        edges = []
        for c in get_registry().components():
            if c.hdn_source:
                edges.append(f"{c.name} → HDN")
            if c.styles_path:
                edges.append(f"{c.name} → CSS")
            for m in c.browser_modules:
                edges.append(f"{c.name} → {_redact(m)}")
        items = "".join(f"<li>{html_lib.escape(e)}</li>" for e in edges)
        return _shell(
            "Graph",
            f"<h2>Component graph</h2><ul>{items or '<li>No edges</li>'}</ul>",
            active="graph",
        )

    @router.get("/security", response_class=HTMLResponse, include_in_schema=False)
    async def security_view() -> str:
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
            active="security",
        )

    @router.get("/a11y", response_class=HTMLResponse, include_in_schema=False)
    async def a11y_view() -> str:
        findings = [
            "Skip link and main landmark present in Explorer shell",
            "Tables use header cells; status is not color-only",
            "Automated axe suites are advisory and do not claim full proof",
        ]
        items = "".join(f"<li>{html_lib.escape(f)}</li>" for f in findings)
        return _shell(
            "Accessibility",
            f"<h2>Accessibility</h2><ul>{items}</ul>",
            active="a11y",
        )

    @router.get("/cache", response_class=HTMLResponse, include_in_schema=False)
    async def cache_view() -> str:
        from hedron_core.cache import CacheTrace

        events = CacheTrace.recent(50)
        rows = "".join(
            "<tr>"
            f"<td>{html_lib.escape(e['kind'])}</td>"
            f"<td><code>{html_lib.escape(e['key_fingerprint'])}</code></td>"
            f"<td>{html_lib.escape(e['scope'])}</td>"
            f"<td>{html_lib.escape(str(e.get('age_ms')))}</td>"
            f"<td>{html_lib.escape(str(e.get('size')))}</td>"
            f"<td>{html_lib.escape(e.get('detail') or '')}</td>"
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
        return _shell("Cache", body, active="cache")

    @router.get("/charts", response_class=HTMLResponse, include_in_schema=False)
    async def charts_view() -> str:
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
        return _shell("Charts", body, active="charts")

    @router.get("/data", response_class=HTMLResponse, include_in_schema=False)
    async def data_view() -> str:
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
        return _shell("Data", body, active="data")

    @router.get("/auto", response_class=HTMLResponse, include_in_schema=False)
    async def auto_view() -> str:
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
        return _shell("Auto", body, active="auto")

    @router.get("/packages", response_class=HTMLResponse, include_in_schema=False)
    async def packages_view() -> str:
        panels = get_explorer_panels()
        items = "".join(
            f"<li><strong>{html_lib.escape(p.title)}</strong> "
            f"({html_lib.escape(p.plugin)}): {html_lib.escape(p.description)}</li>"
            for p in panels
        )
        return _shell(
            "Packages",
            f"<h2>Packages / plugin panels</h2><ul>{items or '<li>No plugin panels</li>'}</ul>",
            active="packages",
        )

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
        return _shell("Settings", body, active="settings")

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
                "hdn_source": _redact(c.hdn_source),
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
            if c.hdn_source:
                edges.append({"from": c.logical_id, "to": _redact(c.hdn_source), "kind": "hdn"})
            if c.styles_path:
                edges.append(
                    {
                        "from": c.logical_id,
                        "to": _redact(c.styles_path),
                        "kind": "styles",
                    }
                )
        return {"nodes": nodes, "edges": edges}

    @router.post("/api/simulate", include_in_schema=False)
    async def api_simulate(request: Request) -> Any:
        try:
            payload = await request.json()
        except Exception:  # noqa: BLE001 — malformed JSON
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
        if policy is not None and getattr(policy, "csrf_enabled", False):
            from hedron_core.csrf import validate_double_submit

            csrf_name = getattr(policy, "csrf_cookie_name", "hedron_csrf")
            cookie = request.cookies.get(csrf_name)
            header_name = getattr(policy, "csrf_header_name", "X-CSRF-Token")
            header = (
                request.headers.get(header_name)
                or request.headers.get("X-CSRF-Token")
                or request.headers.get("X-Hedron-CSRF")
            )
            form_token = None
            validator = getattr(request.app.state, "hedron_csrf_validate", None)
            if callable(validator):
                try:
                    result = validator(request, policy)
                    if hasattr(result, "__await__"):
                        await result  # type: ignore[misc]
                except Exception:  # noqa: BLE001 — FastAPI CSRF raises HTTPException
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
            region_ok = any(
                target == value.split("|", 1)[0] or target.lstrip("#") == rid
                for rid, value in regions.items()
            )
            if not region_ok:
                region_error = f"HX-Target {target!r} is not an authorized fragment region"
        return {
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
                "swap": "innerHTML",
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
        }

    return router


def reset_explorer_runtime_for_tests() -> None:
    """Clear rate-limit / audit state between tests."""
    _TRACE.clear()
    _RATE.clear()
    _AUDIT.clear()
