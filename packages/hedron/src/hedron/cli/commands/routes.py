"""CLI commands: routes, components, preview."""

from __future__ import annotations

import argparse
import json
import sys

from hedron.cli.discovery import _load_app, _registry_empty_hint
from hedron_core.registry import get_registry
from hedron_core.typing_aliases import JsonObject


def _cmd_routes(args: argparse.Namespace) -> int:
    _load_app(args.app)
    try:
        from hedron_explorer.services.catalog import routes_json

        print(json.dumps(routes_json(), indent=2))
        return 0
    except ImportError:
        print("hedron-explorer: skipped (not installed)", file=sys.stderr)
    registry = get_registry()
    rows = [
        {
            "kind": r.kind,
            "name": r.name,
            "path": r.path,
            "methods": list(r.methods),
            "operation_id": r.operation_id,
            "include_in_schema": r.include_in_schema,
            "htmx": dict(r.htmx_inference),
        }
        for r in registry.routes()
    ]
    if not rows:
        _registry_empty_hint(app=args.app, what="routes")
    print(json.dumps(rows, indent=2))
    return 0


def _cmd_components(args: argparse.Namespace) -> int:
    _load_app(args.app)
    registry = get_registry()
    rows: list[JsonObject] = [
        {
            "kind": "component",
            "logical_id": c.logical_id,
            "name": c.name,
            "module": c.module,
            "distribution": c.distribution,
            "styles_path": c.styles_path,
            "style_symbols": dict(c.style_symbols),
            "folder_path": c.folder_path,
        }
        for c in registry.components()
    ]
    rows.extend(
        {
            "kind": "addressable",
            "logical_id": a.logical_id,
            "name": a.name,
            "module": a.module,
            "methods": list(a.methods),
            "route": a.route,
        }
        for a in registry.addressables()
    )
    if not rows:
        _registry_empty_hint(app=args.app, what="components")
    print(json.dumps(rows, indent=2))
    return 0


def _cmd_preview(args: argparse.Namespace) -> int:
    _load_app(args.app)
    registry = get_registry()
    logical_id = args.logical_id
    route = None
    for r in registry.routes():
        if r.logical_id == logical_id or r.name == logical_id:
            route = r
            break
    if route is None:
        print(f"No route found for {logical_id!r}", file=sys.stderr)
        return 1
    payload = {
        "logical_id": route.logical_id,
        "kind": route.kind,
        "path": route.path,
        "methods": list(route.methods),
        "operation_id": route.operation_id,
        "htmx_inference": dict(route.htmx_inference),
        "explanations": [
            f"HTMX inference for this route: {dict(route.htmx_inference)}",
            "Override swap/target via explicit hx-swap / hx-target on the response component.",
            "Production previews use the sealed registry and build manifest when present.",
        ],
        "overrides": {
            "hx-target": "Set explicitly on the component to replace inference",
            "hx-swap": "Set explicitly on the component to replace inference",
        },
        "security_findings": [
            "Internal component resources default to include_in_schema=False",
            "Unsafe cookie-authenticated actions require CSRF",
            "Authenticated fragments use private, no-store caching",
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0
