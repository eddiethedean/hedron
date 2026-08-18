"""Thin Explorer HTTP router. Business logic lives in services/ and views/."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from hedron_explorer.services.catalog import (
    components_json,
    dashboard_graph_json,
    graph_json,
    handle_graph_json,
    interactions_json,
    routes_json,
    security_json,
)
from hedron_explorer.services.diff import current_baseline, diff_baselines
from hedron_explorer.services.health import package_health
from hedron_explorer.services.runtime import (
    RATE,
    explorer_guards,
    prune_explorer_rate,
    reset_explorer_runtime_for_tests,
)
from hedron_explorer.services.simulation import (
    SIMULATE_KEYS,
    click_preview,
    element_simulate,
    redacted_app_scenario,
    simulate,
)
from hedron_explorer.views import pages

__all__ = [
    "explorer_router",
    "reset_explorer_runtime_for_tests",
    "_AUDIT",
    "_TRACE",
    "_RATE",
    "_prune_explorer_rate",
    "_find_component",
    "_hdj_text_under_root",
    "_audit",
    "_SIMULATE_KEYS",
]

from hedron_explorer.services.catalog import find_component as _find_component
from hedron_explorer.services.fs import hdj_text_under_root as _hdj_text_under_root
from hedron_explorer.services.runtime import AUDIT as _AUDIT
from hedron_explorer.services.runtime import TRACE as _TRACE
from hedron_explorer.services.runtime import audit as _audit

_RATE = RATE
_prune_explorer_rate = prune_explorer_rate
_SIMULATE_KEYS = SIMULATE_KEYS


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

    html_pages = (
        ("/", pages.index),
        ("/routes", pages.routes_view),
        ("/graph", pages.graph_view),
        ("/security", pages.security_view),
        ("/a11y", pages.a11y_view),
        ("/cache", pages.cache_view),
        ("/charts", pages.charts_view),
        ("/maps", pages.maps_view),
        ("/extensions", pages.extensions_view),
        ("/data", pages.data_view),
        ("/auto", pages.auto_view),
        ("/packages", pages.packages_view),
        ("/elements", pages.elements_view),
        ("/inventory", pages.inventory_view),
        ("/settings", pages.settings_view),
        ("/interactions", pages.interactions_view),
        ("/features", pages.features_view),
    )
    for path, handler in html_pages:
        router.add_api_route(
            path, handler, methods=["GET"], response_class=HTMLResponse, include_in_schema=False
        )
    router.add_api_route(
        "/component/{name}",
        pages.component_detail,
        methods=["GET"],
        response_class=HTMLResponse,
        include_in_schema=False,
    )
    router.add_api_route(
        "/elements/{logical_id:path}",
        pages.element_detail_view,
        methods=["GET"],
        response_class=HTMLResponse,
        include_in_schema=False,
    )

    @router.get("/api/routes", include_in_schema=False)
    async def api_routes(request: Request) -> Any:
        return routes_json(request)

    @router.get("/api/security", include_in_schema=False)
    async def api_security(request: Request) -> dict[str, Any]:
        return security_json(request)

    @router.get("/api/components", include_in_schema=False)
    async def api_components(request: Request) -> Any:
        return components_json(request)

    @router.get("/api/graph", include_in_schema=False)
    async def api_graph(request: Request) -> dict[str, Any]:
        return graph_json(request)

    @router.get("/api/handle-graph", include_in_schema=False)
    async def api_handle_graph(request: Request) -> dict[str, Any]:
        return handle_graph_json(request)

    @router.get("/api/interactions", include_in_schema=False)
    async def api_interactions(request: Request) -> dict[str, Any]:
        return interactions_json(request)

    @router.get("/api/dashboard-graph", include_in_schema=False)
    async def api_dashboard_graph() -> dict[str, Any]:
        return dashboard_graph_json()

    @router.get("/api/click-preview", include_in_schema=False)
    async def api_click_preview(request: Request) -> Any:
        return await click_preview(request)

    @router.post("/api/simulate", include_in_schema=False)
    async def api_simulate(request: Request) -> Any:
        result = await simulate(request)
        if isinstance(result, JSONResponse):
            return result
        if isinstance(result, dict) and "route" in result:
            result["scenario"] = redacted_app_scenario(
                route=str(result.get("route")), ok=bool(result.get("ok"))
            )
        return result

    @router.post("/api/element-simulate", include_in_schema=False)
    async def api_element_simulate(request: Request) -> Any:
        return await element_simulate(request)

    @router.get("/api/diff", include_in_schema=False)
    async def api_diff() -> dict[str, Any]:
        baseline = current_baseline()
        return diff_baselines(baseline, baseline)

    @router.get("/api/package-health", include_in_schema=False)
    async def api_package_health() -> dict[str, Any]:
        return package_health()

    return router
