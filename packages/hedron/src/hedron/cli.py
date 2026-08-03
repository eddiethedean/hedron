"""Minimal Hedron CLI: routes, components, preview."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from typing import Any

from hedron_core.registry import get_registry

__all__ = ["main"]


def _load_app(app_path: str | None) -> Any | None:
    if not app_path:
        return None
    if ":" not in app_path:
        raise SystemExit("--app must look like 'module.path:attribute'")
    module_name, attr = app_path.split(":", 1)
    module = importlib.import_module(module_name)
    target: Any = module
    for part in attr.split("."):
        target = getattr(target, part)
    if callable(target) and not hasattr(target, "routes"):
        target = target()
    return target


def _cmd_routes(args: argparse.Namespace) -> int:
    _load_app(args.app)
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
    print(json.dumps(rows, indent=2))
    return 0


def _cmd_components(args: argparse.Namespace) -> int:
    _load_app(args.app)
    registry = get_registry()
    rows: list[dict[str, Any]] = [
        {
            "kind": "component",
            "logical_id": c.logical_id,
            "name": c.name,
            "module": c.module,
            "distribution": c.distribution,
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
        "security_findings": [
            "Internal component resources default to include_in_schema=False",
            "Unsafe cookie-authenticated actions require CSRF",
            "Authenticated fragments use private, no-store caching",
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="hedron", description="Hedron inspection CLI")
    parser.add_argument(
        "--app",
        help="Import path to an application factory or instance (module:attr)",
        default=None,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    routes_p = sub.add_parser("routes", help="List registered Hedron routes")
    routes_p.set_defaults(func=_cmd_routes)

    components_p = sub.add_parser("components", help="List registered components")
    components_p.set_defaults(func=_cmd_components)

    preview_p = sub.add_parser("preview", help="Inspect a route/component preview")
    preview_p.add_argument("logical_id", help="Route logical id or name")
    preview_p.set_defaults(func=_cmd_preview)

    args = parser.parse_args(argv)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
