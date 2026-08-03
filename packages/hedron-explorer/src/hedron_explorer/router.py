"""Explorer preview router (development only)."""

from __future__ import annotations

import html as html_lib
from typing import Any

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from hedron_core.registry import get_registry

__all__ = ["explorer_router"]


def explorer_router() -> APIRouter:
    router = APIRouter(tags=["hedron-explorer"])

    @router.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def index() -> str:
        registry = get_registry()
        routes = list(registry.routes())
        components = list(registry.components())
        findings = [
            "Explorer is development-only by default",
            "Secrets and absolute paths are redacted from this view",
            "Internal component resources default to include_in_schema=False",
            "Unsafe cookie-authenticated actions require CSRF validation",
        ]
        route_rows = "".join(
            f"<tr><td>{html_lib.escape(r.kind)}</td>"
            f"<td>{html_lib.escape(r.name)}</td>"
            f"<td><code>{html_lib.escape(r.path)}</code></td>"
            f"<td>{html_lib.escape(','.join(r.methods))}</td>"
            f"<td>{html_lib.escape(str(dict(r.htmx_inference)))}</td></tr>"
            for r in routes
        )
        component_rows = "".join(
            f"<tr><td>{html_lib.escape(c.name)}</td>"
            f"<td><code>{html_lib.escape(c.logical_id)}</code></td>"
            f"<td>{html_lib.escape(c.distribution)}</td></tr>"
            for c in components[:100]
        )
        finding_items = "".join(f"<li>{html_lib.escape(item)}</li>" for item in findings)
        return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Hedron Explorer</title></head>
<body>
  <h1>Hedron Explorer</h1>
  <p>Registry-backed preview for routes, components, HTMX inference, and security findings.</p>
  <h2>Routes</h2>
  <table border="1" cellpadding="6">
    <thead>
      <tr><th>Kind</th><th>Name</th><th>Path</th><th>Methods</th><th>HTMX</th></tr>
    </thead>
    <tbody>{route_rows or "<tr><td colspan='5'>No routes registered</td></tr>"}</tbody>
  </table>
  <h2>Components</h2>
  <table border="1" cellpadding="6">
    <thead><tr><th>Name</th><th>Logical ID</th><th>Distribution</th></tr></thead>
    <tbody>{component_rows or "<tr><td colspan='3'>No components</td></tr>"}</tbody>
  </table>
  <h2>Security findings</h2>
  <ul>{finding_items}</ul>
</body>
</html>"""

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
            ],
            "redacted": True,
        }

    return router
