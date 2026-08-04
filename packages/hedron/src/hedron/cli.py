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


def _apply_project_discovery(base: Path | None = None) -> Any:
    """Load settings, discover folders, and optionally load configured plugins."""
    from hedron.config import load_hedron_settings
    from hedron.plugins import load_plugins
    from hedron_core.discovery import apply_discovery_to_registry, discover_component_folders

    root = (base or Path.cwd()).resolve()
    settings = load_hedron_settings(root)
    discovered = discover_component_folders(settings.resolved_roots(base=root))
    apply_discovery_to_registry(discovered)
    if settings.plugins is not None:
        try:
            load_plugins(enabled=list(settings.plugins))
        except Exception as exc:  # noqa: BLE001 — CLI surfaces plugin errors
            print(f"Plugin load failed: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc
    return settings


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
        dest = out_dir / "template.hdx"
        if dest.exists() and not args.force:
            print(f"Refusing to overwrite {dest} (use --force)", file=sys.stderr)
            return 1
        shutil.copy2(meta.hdn_source, dest)
        written.append(str(dest))
    elif meta.hdn_source is None:
        # Eject a starter HDN shell preserving semantic contract notes
        dest = out_dir / "template.hdx"
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


def _cmd_new(args: argparse.Namespace) -> int:
    dest = Path(args.path or args.name).resolve()
    if dest.exists() and any(dest.iterdir()) and not args.force:
        print(f"Refusing to overwrite non-empty {dest} (use --force)", file=sys.stderr)
        return 1
    guarded = [dest / "app.py", dest / "pyproject.toml"]
    if any(path.exists() for path in guarded) and not args.force:
        existing = ", ".join(str(p) for p in guarded if p.exists())
        print(f"Refusing to overwrite existing {existing} (use --force)", file=sys.stderr)
        return 1
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "components").mkdir(exist_ok=True)
    (dest / "pyproject.toml").write_text(
        f'''[project]
name = "{args.name}"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["hedron>=0.4.0"]

[tool.hedron]
component_roots = ["components"]
theme = "default"
explorer = "off"
''',
        encoding="utf-8",
    )
    (dest / "app.py").write_text(
        """from hedron import Hedron, Page, Text

app = Hedron(
    title="Hedron App",
    security="standard",
    explorer="off",
    session_secret="dev-secret",
)


@app.page("/")
def home() -> Page:
    return Page(Text("Hello from hedron new"), title="Home")
""",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"created": str(dest), "files": ["pyproject.toml", "app.py", "components/"]}, indent=2
        )
    )
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    from hedron_core import (
        DiagnosticSeverity,
        diagnostics_to_json,
        diagnostics_to_sarif,
        diagnostics_to_text,
        meets_severity_threshold,
    )
    from hedron_core.diagnostics import make_diagnostic
    from hedron_core.discovery import discover_component_folders

    _load_app(args.app)
    base = Path(args.project or Path.cwd()).resolve()
    settings = _apply_project_discovery(base)
    diags = []
    # Routes / components presence
    registry = get_registry()
    if not list(registry.components()) and not list(registry.routes()):
        diags.append(
            make_diagnostic(
                "HED-CONFIG-0003",
                severity=DiagnosticSeverity.WARNING,
                title="Empty registry",
                explanation="No components or routes found during check.",
                remediation="Pass --app or discover component folders.",
            )
        )
    # HDN/CSS discovery compile checks
    from hedron_core import HedronError, compile_css, compile_hdn
    from hedron_core.compile_gate import force_runtime_compile

    with force_runtime_compile():
        for item in discover_component_folders(settings.resolved_roots(base=base)):
            if item.styles_css and item.styles_css.is_file():
                try:
                    compile_css(
                        item.styles_css.read_text(encoding="utf-8"),
                        component_id=f"check:{item.name}",
                        registered_roots=[item.folder],
                        component_dir=item.folder,
                    )
                except HedronError as exc:
                    diags.extend(exc.diagnostics)
            if item.template_hdn and item.template_hdn.is_file():
                try:
                    compile_hdn(item.template_hdn.read_text(encoding="utf-8"))
                except HedronError as exc:
                    diags.extend(exc.diagnostics)

    # Security / a11y / freeze-boundary informational findings (excluded from exit code)
    info_diags = [
        make_diagnostic(
            "HED-SEC-0001",
            severity=DiagnosticSeverity.INFORMATION,
            title="CSRF required for unsafe actions",
            explanation="Cookie-authenticated unsafe methods must validate CSRF.",
            remediation="Use HedronRouter.action and standard security profile.",
        ),
        make_diagnostic(
            "HED-A11Y-0001",
            severity=DiagnosticSeverity.INFORMATION,
            title="Run axe for interactive surfaces",
            explanation="Static markup checks do not replace browser accessibility analysis.",
            remediation="Use hedron[browser] axe hooks for Explorer and forms.",
        ),
        make_diagnostic(
            "HED-COMPAT-0001",
            severity=DiagnosticSeverity.INFORMATION,
            title="0.8 feature freeze is active",
            explanation=(
                "Phase 0.8 freezes the public API baseline; no new subsystems, adapters, "
                "or transports. SSE live transport and Django QuerySet DataSource remain Deferred."
            ),
            remediation="See docs/api/STABILITY.md and docs/guides/upgrade.md.",
        ),
        make_diagnostic(
            "HED-COMPAT-0002",
            severity=DiagnosticSeverity.INFORMATION,
            title="Django Supported floor is 5.2 LTS",
            explanation="hedron-django requires Django >=5.2,<6 for Supported adapter claims.",
            remediation="Upgrade Django to the 5.2 LTS line before production adapter use.",
        ),
        make_diagnostic(
            "HED-COMPAT-0003",
            severity=DiagnosticSeverity.INFORMATION,
            title="Interactive Plotly/Altair runtimes are experimental",
            explanation=(
                "Full Plotly/Vega interactive hosts remain experimental until offline pins and "
                "browser evidence promote them; prefer Matplotlib static SVG for stable dashboards."
            ),
            remediation="See docs/api/STABILITY.md and docs/api/CHART.md.",
        ),
        make_diagnostic(
            "HED-COMPAT-0004",
            severity=DiagnosticSeverity.INFORMATION,
            title="Prefer template.hdx for HDN sources",
            explanation=(
                "Component discovery prefers template.hdx; template.hdn remains a compatibility "
                "fallback. hedron eject writes .hdx."
            ),
            remediation=(
                "Rename template.hdn to template.hdx when convenient; see docs/guides/upgrade.md."
            ),
        ),
    ]
    all_diags = [*diags, *info_diags]

    threshold = DiagnosticSeverity(args.severity)
    fmt = args.format
    if fmt == "json":
        print(json.dumps(diagnostics_to_json(all_diags), indent=2))
    elif fmt == "sarif":
        print(json.dumps(diagnostics_to_sarif(all_diags), indent=2))
    else:
        text = diagnostics_to_text(all_diags)
        print(text or "No diagnostics.")
    # Exit on real findings only — evergreen INFORMATION never fails the gate.
    return 1 if meets_severity_threshold(diags, threshold) else 0


def _cmd_graph(args: argparse.Namespace) -> int:
    _load_app(args.app)
    base = Path(getattr(args, "project", None) or Path.cwd()).resolve()
    _apply_project_discovery(base)
    registry = get_registry()
    nodes = []
    edges = []
    for c in registry.components():
        nodes.append({"id": c.logical_id, "name": c.name, "kind": "component"})
        for dep in c.browser_modules:
            edges.append({"from": c.logical_id, "to": dep, "kind": "browser_module"})
        if c.styles_path:
            edges.append({"from": c.logical_id, "to": c.styles_path, "kind": "styles"})
        if c.hdn_source:
            edges.append({"from": c.logical_id, "to": c.hdn_source, "kind": "hdn"})
    inverse: dict[str, list[str]] = {}
    for edge in edges:
        inverse.setdefault(str(edge["to"]), []).append(str(edge["from"]))
    payload = {"nodes": nodes, "edges": edges, "inverse_consumers": inverse}
    print(json.dumps(payload, indent=2))
    return 0


def _cmd_audit_components(args: argparse.Namespace) -> int:
    _load_app(args.app)
    base = Path(getattr(args, "project", None) or Path.cwd()).resolve()
    _apply_project_discovery(base)
    from hedron_core.plugins import get_diagnostic_owners, get_explorer_panels

    registry = get_registry()
    rows = []
    for c in registry.components():
        rows.append(
            {
                "logical_id": c.logical_id,
                "name": c.name,
                "distribution": c.distribution,
                "module": c.module,
                "capabilities": {
                    "hdn": bool(c.hdn_source),
                    "styles": bool(c.styles_path),
                    "browser_js": bool(c.browser_modules),
                    "assets": bool(c.asset_roots),
                },
            }
        )
    plugin_rows: list[dict[str, Any]] = []
    try:
        from importlib.metadata import entry_points

        from hedron.plugins import ENTRY_POINT_GROUP

        eps = entry_points()
        discovered = (
            list(eps.select(group=ENTRY_POINT_GROUP))
            if hasattr(eps, "select")
            else list(eps.get(ENTRY_POINT_GROUP, []))  # type: ignore[arg-type]
        )
        for ep in discovered:
            try:
                target = ep.load()
                meta = getattr(target, "PLUGIN_META", None)
                if meta is not None:
                    plugin_rows.append(meta.to_dict())
                else:
                    plugin_rows.append({"name": ep.name, "version": "unknown"})
            except Exception as exc:  # noqa: BLE001
                plugin_rows.append({"name": ep.name, "error": str(exc)})
    except Exception:  # noqa: BLE001
        plugin_rows = []
    payload = {
        "components": rows,
        "plugins": plugin_rows,
        "explorer_panels": [p.to_dict() for p in get_explorer_panels()],
        "diagnostic_owners": dict(get_diagnostic_owners()),
    }
    print(json.dumps(payload, indent=2))
    return 0


def _cmd_dev(args: argparse.Namespace) -> int:
    from hedron.build import run_build
    from hedron.config import load_hedron_settings

    base = Path(args.project or Path.cwd()).resolve()
    settings = load_hedron_settings(base)
    roots = list(settings.resolved_roots(base=base))
    watch_exts = {
        ".hdx",
        ".hdn",
        ".css",
        ".mjs",
        ".js",
        ".png",
        ".svg",
        ".jpg",
        ".jpeg",
        ".webp",
    }
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

    new_p = sub.add_parser("new", help="Scaffold a new Hedron application")
    new_p.add_argument("name", help="Project name")
    new_p.add_argument("--path", default=None, help="Destination directory")
    new_p.add_argument("--force", action="store_true")
    new_p.set_defaults(func=_cmd_new)

    check_p = sub.add_parser("check", help="Run project diagnostics")
    check_p.add_argument("--project", default=None)
    check_p.add_argument(
        "--format",
        choices=("text", "json", "sarif"),
        default="text",
    )
    check_p.add_argument(
        "--severity",
        choices=("error", "warning", "information"),
        default="error",
        help="Fail when diagnostics meet or exceed this severity",
    )
    check_p.set_defaults(func=_cmd_check)

    graph_p = sub.add_parser("graph", help="Component dependency graph")
    graph_p.set_defaults(func=_cmd_graph)

    audit_p = sub.add_parser("audit-components", help="Capability and package audit")
    audit_p.set_defaults(func=_cmd_audit_components)

    dev_p = sub.add_parser("dev", help="Watch HDN/CSS/assets and rebuild atomically")
    dev_p.add_argument("--project", default=None)
    dev_p.add_argument("--interval", type=float, default=0.5)
    dev_p.add_argument("--once", action="store_true", help="Build once and exit")
    dev_p.set_defaults(func=_cmd_dev)

    args = parser.parse_args(argv)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
