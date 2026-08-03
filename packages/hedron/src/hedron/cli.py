"""Hedron CLI: routes, components, preview, build, dev, inspect, eject."""

from __future__ import annotations

import argparse
import importlib
import json
import shutil
import sys
import time
from pathlib import Path
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


def _registry_empty_hint(*, app: str | None, what: str) -> None:
    if app:
        return
    registry = get_registry()
    if registry.components() or registry.routes() or registry.addressables():
        return
    print(
        f"No {what} found. Pass --app module:attr to load an application "
        "before inspecting the registry.",
        file=sys.stderr,
    )


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
    if not rows:
        _registry_empty_hint(app=args.app, what="routes")
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
            "styles_path": c.styles_path,
            "hdn_source": c.hdn_source,
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
        "security_findings": [
            "Internal component resources default to include_in_schema=False",
            "Unsafe cookie-authenticated actions require CSRF",
            "Authenticated fragments use private, no-store caching",
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0


def _find_component(name: str) -> Any:
    registry = get_registry()
    for c in registry.components():
        if c.logical_id == name or c.name == name or c.logical_id.endswith(f".{name}"):
            return c
    return None


def _cmd_inspect(args: argparse.Namespace) -> int:
    _load_app(args.app)
    from hedron.config import load_hedron_settings
    from hedron_core.discovery import apply_discovery_to_registry, discover_component_folders

    settings = load_hedron_settings(Path.cwd())
    discovered = discover_component_folders(settings.resolved_roots(base=Path.cwd()))
    apply_discovery_to_registry(discovered)

    meta = _find_component(args.component)
    if meta is None:
        _registry_empty_hint(app=args.app, what="components")
        print(f"Component {args.component!r} not found", file=sys.stderr)
        return 1
    payload: dict[str, Any] = {
        "logical_id": meta.logical_id,
        "name": meta.name,
        "module": meta.module,
        "distribution": meta.distribution,
        "props_model": meta.props_model,
        "slots": dict(meta.slots),
        "styles_path": meta.styles_path,
        "hdn_source": meta.hdn_source,
        "style_symbols": dict(meta.style_symbols),
        "browser_modules": list(meta.browser_modules),
        "folder_path": meta.folder_path,
        "accessibility_notes": meta.accessibility_notes,
    }
    if meta.hdn_source and Path(meta.hdn_source).is_file():
        payload["template"] = Path(meta.hdn_source).read_text(encoding="utf-8")
    if meta.styles_path and Path(meta.styles_path).is_file():
        payload["styles"] = Path(meta.styles_path).read_text(encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


def _cmd_eject(args: argparse.Namespace) -> int:
    _load_app(args.app)
    from hedron.config import load_hedron_settings
    from hedron_core.discovery import apply_discovery_to_registry, discover_component_folders

    settings = load_hedron_settings(Path.cwd())
    discovered = discover_component_folders(settings.resolved_roots(base=Path.cwd()))
    apply_discovery_to_registry(discovered)

    meta = _find_component(args.component)
    if meta is None:
        _registry_empty_hint(app=args.app, what="components")
        print(f"Component {args.component!r} not found", file=sys.stderr)
        return 1
    out_dir = Path(args.out or meta.folder_path or f"components/{meta.name}")
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    if meta.hdn_source and Path(meta.hdn_source).is_file():
        dest = out_dir / "template.hdn"
        if dest.exists() and not args.force:
            print(f"Refusing to overwrite {dest} (use --force)", file=sys.stderr)
            return 1
        shutil.copy2(meta.hdn_source, dest)
        written.append(str(dest))
    elif meta.hdn_source is None:
        # Eject a starter HDN shell preserving semantic contract notes
        dest = out_dir / "template.hdn"
        if not dest.exists() or args.force:
            dest.write_text(
                f"<!-- Ejected template for {meta.logical_id}. -->\n"
                f"<!-- Preserve props/slots contracts for {meta.name}. -->\n"
                f'<div class="root">{{label}}</div>\n',
                encoding="utf-8",
            )
            written.append(str(dest))
    if meta.styles_path and Path(meta.styles_path).is_file():
        dest = out_dir / "styles.css"
        if dest.exists() and not args.force:
            print(f"Refusing to overwrite {dest} (use --force)", file=sys.stderr)
            return 1
        shutil.copy2(meta.styles_path, dest)
        written.append(str(dest))
    elif meta.styles_path is None:
        dest = out_dir / "styles.css"
        if not dest.exists() or args.force:
            dest.write_text(
                f"/* Ejected styles for {meta.logical_id} */\n.root {{\n  display: block;\n}}\n",
                encoding="utf-8",
            )
            written.append(str(dest))
    if not written:
        print(
            f"Nothing written for {meta.logical_id!r} "
            "(sources missing and starter files already present; use --force).",
            file=sys.stderr,
        )
        return 1
    print(json.dumps({"component": meta.logical_id, "written": written}, indent=2))
    return 0


def _cmd_build(args: argparse.Namespace) -> int:
    from hedron.build import run_build
    from hedron.config import load_hedron_settings

    base = Path(args.project or Path.cwd()).resolve()
    settings = load_hedron_settings(base)
    result = run_build(project_dir=base, settings=settings, production=not args.dev)
    print(
        json.dumps(
            {
                "build_dir": str(result.build_dir),
                "digest": result.manifest.digest or result.manifest.to_dict()["digest"],
                "theme": result.manifest.theme,
                "assets": len(result.manifest.assets.assets),
            },
            indent=2,
        )
    )
    return 0


def _cmd_dev(args: argparse.Namespace) -> int:
    from hedron.build import run_build
    from hedron.config import load_hedron_settings

    base = Path(args.project or Path.cwd()).resolve()
    settings = load_hedron_settings(base)
    roots = list(settings.resolved_roots(base=base))
    watch_exts = {".hdn", ".css", ".mjs", ".js", ".png", ".svg", ".jpg", ".jpeg", ".webp"}
    print(f"hedron dev watching {roots or [base]} (Ctrl+C to stop)", file=sys.stderr)
    result = run_build(project_dir=base, settings=settings, production=False)
    print(f"initial build → {result.build_dir}", file=sys.stderr)
    if args.once:
        return 0
    mtimes: dict[Path, float] = {}

    def snapshot() -> dict[Path, float]:
        current: dict[Path, float] = {}
        search_roots = roots or [base]
        for root in search_roots:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if path.is_file() and path.suffix.lower() in watch_exts:
                    current[path] = path.stat().st_mtime
        return current

    mtimes = snapshot()
    try:
        while True:
            time.sleep(args.interval)
            current = snapshot()
            if current != mtimes:
                mtimes = current
                try:
                    result = run_build(project_dir=base, settings=settings, production=False)
                    print(f"rebuilt → {result.build_dir}", file=sys.stderr)
                except Exception as exc:
                    print(f"build failed (previous output retained): {exc}", file=sys.stderr)
    except KeyboardInterrupt:
        print("stopped", file=sys.stderr)
        return 0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="hedron", description="Hedron CLI")
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

    inspect_p = sub.add_parser("inspect", help="Explain a component template/styles/deps")
    inspect_p.add_argument("component", help="Component name or logical id")
    inspect_p.set_defaults(func=_cmd_inspect)

    eject_p = sub.add_parser("eject", help="Eject editable local HDN/CSS overrides")
    eject_p.add_argument("component", help="Component name or logical id")
    eject_p.add_argument("--out", help="Output directory")
    eject_p.add_argument("--force", action="store_true")
    eject_p.set_defaults(func=_cmd_eject)

    build_p = sub.add_parser("build", help="Compile HDN/CSS/assets into a build manifest")
    build_p.add_argument("--project", default=None)
    build_p.add_argument("--dev", action="store_true", help="Use readable development names")
    build_p.set_defaults(func=_cmd_build)

    dev_p = sub.add_parser("dev", help="Watch HDN/CSS/assets and rebuild atomically")
    dev_p.add_argument("--project", default=None)
    dev_p.add_argument("--interval", type=float, default=0.5)
    dev_p.add_argument("--once", action="store_true", help="Build once and exit")
    dev_p.set_defaults(func=_cmd_dev)

    args = parser.parse_args(argv)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
