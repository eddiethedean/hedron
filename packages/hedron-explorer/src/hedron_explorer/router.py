"""Component Explorer router with HTMX panels (phase 0.4)."""

from __future__ import annotations

import html as html_lib
import time
from collections import deque
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from hedron_core.plugins import get_explorer_panels
from hedron_core.registry import get_registry
from hedron_core.rendering import RenderMode, render

__all__ = ["explorer_router"]

_TRACE: deque[dict[str, Any]] = deque(maxlen=100)
_RATE: dict[str, list[float]] = {}
_AUDIT: deque[dict[str, Any]] = deque(maxlen=200)


def _redact(value: str | None) -> str | None:
    if value is None:
        return None
    if "/" in value or "\\" in value:
        return Path(value).name
    return value


def _audit(event: str, **payload: Any) -> None:
    _AUDIT.appendleft({"event": event, **payload, "ts": time.time()})


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
    if static_dir.is_dir():
        router.mount(
            "/static",
            StaticFiles(directory=str(static_dir)),
            name="hedron-explorer-static",
        )

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
    async def component_detail(name: str) -> str:
        meta = None
        for c in get_registry().components():
            if c.name == name or c.logical_id.endswith(f".{name}"):
                meta = c
                break
        if meta is None:
            return _shell("Missing", f"<p>Unknown component {html_lib.escape(name)}</p>")
        hdn = ""
        styles = ""
        if meta.hdn_source and Path(meta.hdn_source).is_file():
            hdn = Path(meta.hdn_source).read_text(encoding="utf-8")
        if meta.styles_path and Path(meta.styles_path).is_file():
            styles = Path(meta.styles_path).read_text(encoding="utf-8")
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
          <div class="preview">{preview_html}</div>
        </section>
        <section>
          <h3>Inference explanations</h3>
          <ul>{"".join(f"<li>{html_lib.escape(x)}</li>" for x in explanations)}</ul>
        </section>
        <section>
          <h3>Source / HDN</h3>
          <pre>{html_lib.escape(hdn or "(no template.hdn)")}</pre>
        </section>
        <section>
          <h3>Styles</h3>
          <pre>{html_lib.escape(styles or "(no styles.css)")}</pre>
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
        payload = await request.json()
        if payload.get("allow_mutations"):
            return JSONResponse(
                {"detail": "Mutation simulation is disabled by default"},
                status_code=403,
            )
        name = payload.get("route")
        routes = {r.name: r for r in get_registry().routes()}
        if name not in routes:
            return JSONResponse(
                {"detail": "Unregistered route identifier"},
                status_code=400,
            )
        _TRACE.appendleft({"kind": "simulate", "route": name, "mutations": False})
        return {"ok": True, "route": name, "mutations": False}

    return router
