"""Hedron CLI: routes, components, preview, build, dev, inspect, eject."""

from __future__ import annotations

import argparse
import ast
import importlib
import json
import re
import shutil
import sys
import time
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Any, cast

from hedron.config import HedronSettings
from hedron_core.registry import ComponentMeta, get_registry
from hedron_core.typing_aliases import JsonObject, PluginMetaDict

__all__ = ["main"]


@lru_cache(maxsize=1)
def _release_pin_bounds() -> tuple[str, str]:
    """Return ``(pin_floor, pin_ceiling)`` for scaffold dependency pins.

    Prefer ``docs/release.toml`` when running from a monorepo checkout. Fall back to
    this package's ``__version__`` as the floor (published wheels) and the next
    minor train as the ceiling.
    """
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "docs" / "release.toml"
        if not candidate.is_file():
            continue
        release = tomllib.loads(candidate.read_text(encoding="utf-8")).get("release", {})
        floor = str(release.get("pin_floor", "")).strip()
        ceiling = str(release.get("pin_ceiling", "")).strip()
        if floor and ceiling:
            return floor, ceiling
    from hedron import __version__ as package_version

    parts = package_version.split(".")
    if len(parts) < 2 or not parts[1].isdigit():
        raise RuntimeError(f"cannot derive scaffold pin from version {package_version!r}")
    return package_version, f"0.{int(parts[1]) + 1}"


def _scaffold_dep(package: str) -> str:
    floor, ceiling = _release_pin_bounds()
    return f"{package}>={floor},<{ceiling}"


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


def _apply_project_discovery(base: Path | None = None) -> HedronSettings:
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
        except Exception as exc:
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


def _find_component(name: str) -> ComponentMeta | None:
    registry = get_registry()
    aliases = {"NavLink": "HtmxLink"}
    wanted = {name, aliases.get(name, name)}
    for c in registry.components():
        if c.logical_id == name or c.name in wanted or c.logical_id.endswith(f".{name}"):
            return c
        if any(c.logical_id.endswith(f".{alias}") for alias in wanted):
            return c
    return None


def _accessibility_contract_for(meta: object) -> Any:
    """Prefer curated reviewed contracts; fall back to an unreviewed stub."""
    from hedron_core.a11y import (
        AccessibilityContractCatalog,
        default_contract,
        seed_reviewed_contracts,
    )

    name = str(getattr(meta, "name", "") or "")
    package = getattr(meta, "distribution", None)
    pkg = package if isinstance(package, str) else "hedron-core"
    notes = str(getattr(meta, "accessibility_notes", None) or "")
    catalog = AccessibilityContractCatalog(package=pkg)
    seed_reviewed_contracts(catalog, package=pkg)
    catalog.ensure_registry(package=pkg)
    existing = catalog.contracts.get(name)
    if existing is not None:
        return existing
    return default_contract(name, package=pkg, notes=notes)


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
    contract = _accessibility_contract_for(meta)
    payload: JsonObject = {
        "logical_id": meta.logical_id,
        "name": meta.name,
        "module": meta.module,
        "distribution": meta.distribution,
        "props_model": meta.props_model,
        "slots": dict(meta.slots),
        "styles_path": meta.styles_path,
        "style_symbols": dict(meta.style_symbols),
        "browser_modules": list(meta.browser_modules),
        "folder_path": meta.folder_path,
        "accessibility_notes": meta.accessibility_notes,
        "accessibility_contract": contract.as_dict(),
        "accessibility_props_alongside_ordinary": True,
        "repair_guidance": {
            "reversible": True,
            "author_reviewed": True,
            "default_on": True,
        },
    }
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
    # Never trust registry ``folder_path`` as a write root (same policy as Explorer reads).
    cwd = Path.cwd().resolve()
    if args.out:
        out_dir = Path(args.out).expanduser().resolve()
        try:
            out_dir.relative_to(cwd)
        except ValueError:
            print(
                f"Refusing to eject outside the project root: {out_dir}",
                file=sys.stderr,
            )
            return 1
    else:
        out_dir = cwd / "components" / meta.name
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    contract = _accessibility_contract_for(meta)
    contract_path = out_dir / "accessibility_contract.json"
    if contract_path.exists() and not args.force:
        print(f"Refusing to overwrite {contract_path} (use --force)", file=sys.stderr)
        return 1
    contract_path.write_text(
        json.dumps(contract.as_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
    written.append(str(contract_path))
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
    framework = "fastapi"
    if getattr(args, "flask", False):
        framework = "flask"
    if getattr(args, "django", False):
        framework = "django"
    if getattr(args, "flask", False) and getattr(args, "django", False):
        print("Choose at most one of --flask / --django", file=sys.stderr)
        return 1

    if framework == "fastapi" or framework == "flask":
        guarded = [dest / "app.py", dest / "pyproject.toml"]
    else:
        guarded = [dest / "manage.py", dest / "pyproject.toml", dest / "project"]
    if any(path.exists() for path in guarded) and not args.force:
        existing = ", ".join(str(p) for p in guarded if p.exists())
        print(f"Refusing to overwrite existing {existing} (use --force)", file=sys.stderr)
        return 1
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "components").mkdir(exist_ok=True)

    if framework == "fastapi":
        return _scaffold_fastapi(args, dest)
    if framework == "flask":
        return _scaffold_flask(args, dest)
    return _scaffold_django(args, dest)


def _scaffold_fastapi(args: argparse.Namespace, dest: Path) -> int:
    (dest / "pyproject.toml").write_text(
        f'''[project]
name = "{args.name}"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "{_scaffold_dep("hedron")}",
    "uvicorn[standard]>=0.30",
]

[tool.hedron]
component_roots = ["components"]
theme = "default"
explorer = "off"
''',
        encoding="utf-8",
    )
    (dest / "app.py").write_text(
        """import os
from datetime import UTC, datetime

from hedron import Hedron, Page, RefreshButton, Stack, Text, html, swap

app = Hedron(
    title="Hedron App",
    security="standard",
    explorer="off",
    session_secret=os.environ.get(
        "HEDRON_SESSION_SECRET", "replace-in-production"
    ),
)

status = app.region("service-status", description="Live status panel")


def status_panel():
    stamp = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"All systems operational · refreshed {stamp}"),
        id=status.id,
        role="status",
        aria={"live": "polite"},
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Text("Hello from hedron new"),
            status_panel(),
            RefreshButton.for_region(status, href="/status", label="Refresh status"),
        ),
        title="Home",
    )


@app.fragment("/status", region=status)
def refresh_status():
    return swap(status_panel())
""",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "created": str(dest),
                "framework": "fastapi",
                "files": ["pyproject.toml", "app.py", "components/"],
            },
            indent=2,
        )
    )
    return 0


def _scaffold_flask(args: argparse.Namespace, dest: Path) -> int:
    (dest / "pyproject.toml").write_text(
        f'''[project]
name = "{args.name}"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "{_scaffold_dep("hedron-flask")}",
    "{_scaffold_dep("hedron-core")}",
    "flask>=3,<4",
]

[tool.hedron]
component_roots = ["components"]
''',
        encoding="utf-8",
    )
    (dest / "app.py").write_text(
        """import os
from datetime import UTC, datetime

from hedron_core import FragmentRegion, InteractionResult, Page, Text, html
from hedron_core.interaction import InteractionPolicy
from hedron_flask import HedronFlask

app = HedronFlask(__name__, security="standard")
assert app.flask is not None
app.flask.config["SECRET_KEY"] = os.environ.get(
    "HEDRON_SESSION_SECRET", "replace-in-production"
)

PANEL = FragmentRegion(id="panel", selector="#panel")


def panel_body() -> object:
    stamp = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return html.div(Text(f"Flask status · {stamp}"), id="panel")


@app.page("/")
def home() -> Page:
    return Page(
        html.div(
            Text("Hello from hedron new --flask"),
            panel_body(),
            html.button(
                Text("Refresh"),
                **{
                    "hx-get": "/status",
                    "hx-target": "#panel",
                    "hx-swap": "outerHTML",
                },
            ),
        ),
        title="Home",
    )


@app.component("/status", fragment_regions=(PANEL,))
def status() -> InteractionResult:
    return InteractionResult(
        content=panel_body(),
        region_id="panel",
        policy=InteractionPolicy(declared_regions=(PANEL,)),
    )


# WSGI entry: `flask --app app run` uses module-level Flask app
flask_app = app.flask
""",
        encoding="utf-8",
    )
    (dest / "README.md").write_text(
        "# Hedron Flask app\n\n"
        "Set `HEDRON_SESSION_SECRET` before production. "
        "Under `HEDRON_ENV=production`, placeholder secrets are refused "
        "unless listed in `HEDRON_SECURITY_RISK_ACCEPTANCE`.\n\n"
        "```bash\nuv sync && uv run flask --app app run\n```\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "created": str(dest),
                "framework": "flask",
                "files": ["pyproject.toml", "app.py", "README.md", "components/"],
            },
            indent=2,
        )
    )
    return 0


def _scaffold_django(args: argparse.Namespace, dest: Path) -> int:
    (dest / "pyproject.toml").write_text(
        f'''[project]
name = "{args.name}"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "{_scaffold_dep("hedron-django")}",
    "{_scaffold_dep("hedron-core")}",
    "django>=5.2,<6",
    "waitress>=3,<4",
]

[tool.hedron]
component_roots = ["components"]
''',
        encoding="utf-8",
    )
    project = dest / "project"
    project.mkdir(exist_ok=True)
    (project / "__init__.py").write_text("", encoding="utf-8")
    (project / "settings.py").write_text(
        """import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production")
# Default off; set DJANGO_DEBUG=1 for local development.
DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "hedron_django",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "hedron_django.middleware.HedronSecurityHeadersMiddleware",
]
ROOT_URLCONF = "project.urls"
TEMPLATES = []
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
STATIC_URL = "static/"
HEDRON_SECURITY_PROFILE = "standard"
# Accept portable Hedron HTMX CSRF header (X-CSRF-Token) with stock CsrfViewMiddleware.
CSRF_HEADER_NAME = "HTTP_X_CSRF_TOKEN"
""",
        encoding="utf-8",
    )
    (project / "urls.py").write_text(
        """from datetime import UTC, datetime

from django.urls import path
from hedron_core import FragmentRegion, InteractionResult, Page, Text, html
from hedron_core.interaction import InteractionPolicy
from hedron_django import hedron_static_urlpatterns, hedron_view

PANEL = FragmentRegion(id="panel", selector="#panel")


def panel_body():
    stamp = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return html.div(Text(f"Django status · {stamp}"), id="panel")


@hedron_view(fragment_regions=(PANEL,))
def home(request):
    return Page(
        html.div(
            Text("Hello from hedron new --django"),
            panel_body(),
            html.button(
                Text("Refresh"),
                **{
                    "hx-get": "/status",
                    "hx-target": "#panel",
                    "hx-swap": "outerHTML",
                },
            ),
        ),
        title="Home",
    )


@hedron_view(fragment_regions=(PANEL,))
def status(request):
    return InteractionResult(
        content=panel_body(),
        region_id="panel",
        policy=InteractionPolicy(declared_regions=(PANEL,)),
    )


urlpatterns = [
    *hedron_static_urlpatterns(),
    path("", home, name="home"),
    path("status", status, name="status"),
]
""",
        encoding="utf-8",
    )
    (dest / "manage.py").write_text(
        """#!/usr/bin/env python
import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
""",
        encoding="utf-8",
    )
    (dest / "wsgi.py").write_text(
        """import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
application = get_wsgi_application()
""",
        encoding="utf-8",
    )
    (dest / "README.md").write_text(
        "# Hedron Django app\n\n"
        "Set `HEDRON_SESSION_SECRET` before production. "
        "Placeholder secrets are refused under `HEDRON_ENV=production` "
        "unless accepted via `HEDRON_SECURITY_RISK_ACCEPTANCE`.\n\n"
        "```bash\nuv sync && uv run waitress-serve --port=8000 wsgi:application\n```\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "created": str(dest),
                "framework": "django",
                "files": [
                    "pyproject.toml",
                    "manage.py",
                    "wsgi.py",
                    "project/",
                    "README.md",
                    "components/",
                ],
            },
            indent=2,
        )
    )
    return 0


def _declared_selectors_for_routes() -> dict[str, set[str]]:
    """Map route path → authorized selectors/ids from registry endpoints."""
    declared: dict[str, set[str]] = {}
    for route in get_registry().routes():
        selectors: set[str] = set()
        regions = getattr(route.endpoint, "_hedron_fragment_regions", None) or ()
        for region in regions:
            selectors.add(region.selector)
        inference = dict(getattr(route, "htmx_inference", {}) or {})
        raw = inference.get("fragment_regions") or ""
        if isinstance(raw, str) and raw.startswith("{"):
            import ast

            try:
                parsed = ast.literal_eval(raw)
            except (SyntaxError, ValueError):
                parsed = {}
            if isinstance(parsed, dict):
                for _rid, value in parsed.items():
                    selector = str(value).split("|", 1)[0]
                    selectors.add(selector)
        if selectors:
            declared[route.path] = selectors
    return declared


def _scan_refresh_button_targets(base: Path) -> list[tuple[str, str | None, str | None, str]]:
    """AST-light scan for RefreshButton(target=..., href=...) / for_region mismatches."""
    findings: list[tuple[str, str | None, str | None, str]] = []
    skip = {".venv", "node_modules", "dist", "site-packages", ".git"}
    for path in sorted(base.rglob("*.py")):
        if any(part in skip or part.startswith(".") for part in path.parts):
            continue
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            is_for_region = isinstance(func, ast.Attribute) and func.attr == "for_region"
            is_refresh = isinstance(func, ast.Name) and func.id == "RefreshButton"
            is_refresh_attr = (
                isinstance(func, ast.Attribute)
                and func.attr == "RefreshButton"
                and not is_for_region
            )
            if not (is_for_region or is_refresh or is_refresh_attr):
                continue
            href: str | None = None
            target: str | None = None
            for kw in node.keywords:
                if (
                    kw.arg == "href"
                    and isinstance(kw.value, ast.Constant)
                    and isinstance(kw.value.value, str)
                ):
                    href = kw.value.value
                if (
                    kw.arg == "target"
                    and isinstance(kw.value, ast.Constant)
                    and isinstance(kw.value.value, str)
                ):
                    target = kw.value.value
            # for_region(region, href=...) — region may be Name; record href only
            findings.append(
                (str(path), href, target, "for_region" if is_for_region else "RefreshButton")
            )
    return findings


def _check_htmx_region_mismatches(base: Path) -> list[Any]:
    """Detect RefreshButton hx-target that does not match declared route regions."""
    from hedron_core import DiagnosticSeverity
    from hedron_core.codes import HED_HTMX_0001
    from hedron_core.diagnostics import make_diagnostic

    declared = _declared_selectors_for_routes()
    if not declared:
        return []
    diags = []
    for file_path, href, target, kind in _scan_refresh_button_targets(base):
        if not href or not target:
            continue
        allowed = declared.get(href)
        if allowed is None:
            continue
        if target not in allowed:
            diags.append(
                make_diagnostic(
                    HED_HTMX_0001,
                    severity=DiagnosticSeverity.WARNING,
                    title="HX-Target / region mismatch",
                    explanation=(
                        f"{kind} in {file_path} targets {target!r} for {href!r}, "
                        f"but declared regions are {sorted(allowed)}."
                    ),
                    remediation=(
                        "Use RefreshButton.for_region(region, href=...) or align "
                        "target= with @app.fragment(..., region=...) / fragment_regions=."
                    ),
                    context={"href": href, "target": target, "declared": sorted(allowed)},
                )
            )
    return diags


def _ast_str_kw(node: Any, name: str) -> str | None:
    for kw in getattr(node, "keywords", ()):
        if (
            kw.arg == name
            and isinstance(kw.value, ast.Constant)
            and isinstance(kw.value.value, str)
        ):
            return kw.value.value
    return None


def _ast_call_name(func: Any) -> str | None:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _scan_select_oob_and_oob_updates(
    base: Path,
) -> list[tuple[str, frozenset[str], frozenset[str], frozenset[str]]]:
    """Per-file ``select_oob`` ids, ``OobUpdate`` bound ids, and unparsed tokens."""
    from hedron_core.interaction import OobUpdate as _OobUpdate
    from hedron_core.interaction import (
        oob_update_element_ids,
        parse_select_oob_element_ids,
        unparsed_select_oob_tokens,
    )

    findings: list[tuple[str, frozenset[str], frozenset[str], frozenset[str]]] = []
    skip = {".venv", "node_modules", "dist", "site-packages", ".git"}
    select_oob_call_names = {
        "HtmxLink",
        "NavLink",
        "Hx",
        "Form",
        "Button",
        "RefreshButton",
    }
    for path in sorted(base.rglob("*.py")):
        if any(part in skip or part.startswith(".") for part in path.parts):
            continue
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        select_oob_ids: set[str] = set()
        oob_ids: set[str] = set()
        unparsed: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = _ast_call_name(node.func)
                if name in select_oob_call_names:
                    select_oob = _ast_str_kw(node, "select_oob")
                    if select_oob is None:
                        select_oob = _ast_str_kw(node, "hx_select_oob")
                    if select_oob:
                        select_oob_ids.update(parse_select_oob_element_ids(select_oob))
                        unparsed.update(unparsed_select_oob_tokens(select_oob))
                elif name == "OobUpdate":
                    element_id = _ast_str_kw(node, "element_id")
                    select = _ast_str_kw(node, "select")
                    update = _OobUpdate(content="", element_id=element_id, select=select)
                    oob_ids.update(oob_update_element_ids((update,)))
                # Hx(**{"hx-select-oob": "..."}) / raw kwargs via keywords with Constant keys
                for kw in node.keywords:
                    if kw.arg is None and isinstance(kw.value, ast.Dict):
                        for key, value in zip(kw.value.keys, kw.value.values, strict=False):
                            if (
                                isinstance(key, ast.Constant)
                                and key.value in {"hx-select-oob", "select_oob"}
                                and isinstance(value, ast.Constant)
                                and isinstance(value.value, str)
                            ):
                                select_oob_ids.update(parse_select_oob_element_ids(value.value))
                                unparsed.update(unparsed_select_oob_tokens(value.value))
                    elif (
                        kw.arg in {"select_oob", "hx_select_oob"}
                        and isinstance(kw.value, ast.Constant)
                        and isinstance(kw.value.value, str)
                    ):
                        # Already handled for named calls above; still catch unknown wrappers.
                        select_oob_ids.update(parse_select_oob_element_ids(kw.value.value))
                        unparsed.update(unparsed_select_oob_tokens(kw.value.value))
            elif isinstance(node, ast.Dict):
                for key, value in zip(node.keys, node.values, strict=False):
                    if (
                        isinstance(key, ast.Constant)
                        and key.value == "hx-select-oob"
                        and isinstance(value, ast.Constant)
                        and isinstance(value.value, str)
                    ):
                        select_oob_ids.update(parse_select_oob_element_ids(value.value))
                        unparsed.update(unparsed_select_oob_tokens(value.value))
        if (select_oob_ids and oob_ids) or unparsed:
            findings.append(
                (str(path), frozenset(select_oob_ids), frozenset(oob_ids), frozenset(unparsed))
            )
    return findings


def _check_select_oob_conflicts(base: Path) -> list[Any]:
    """Error when the same id is used with both ``select_oob`` and ``OobUpdate``."""
    from hedron_core import DiagnosticSeverity
    from hedron_core.codes import HED_HTMX_0002
    from hedron_core.diagnostics import make_diagnostic
    from hedron_core.interaction import conflicting_select_oob_targets

    diags = []
    for file_path, select_ids, oob_ids, unparsed in _scan_select_oob_and_oob_updates(base):
        select_oob = ",".join(f"#{item}" for item in sorted(select_ids))
        conflicts = conflicting_select_oob_targets(select_oob, oob_ids=oob_ids)
        if conflicts:
            targets = ", ".join(f"#{item}" for item in sorted(conflicts))
            diags.append(
                make_diagnostic(
                    HED_HTMX_0002,
                    severity=DiagnosticSeverity.ERROR,
                    title="select_oob / OobUpdate same-target conflict",
                    explanation=(
                        f"{file_path} uses both select_oob / hx-select-oob and "
                        f"OobUpdate for {targets}. Combining hx-select-oob with a "
                        "server hx-swap-oob envelope for the same id can replace a "
                        "semantic shell host (for example <nav aria-label=...>) with "
                        "Hedron's OOB wrapper."
                    ),
                    remediation=(
                        "Use one OOB mechanism per target. Prefer explicit OobUpdate "
                        "with swap='innerHTML' (the default) and omit matching "
                        "select_oob so the existing host tag and aria-* attributes "
                        "are preserved. OobUpdate(tag=...) is defense in depth only."
                    ),
                    context={
                        "path": file_path,
                        "conflicts": sorted(conflicts),
                        "select_oob_ids": sorted(select_ids),
                        "oob_ids": sorted(oob_ids),
                    },
                )
            )
        if unparsed:
            tokens = ", ".join(sorted(unparsed))
            diags.append(
                make_diagnostic(
                    HED_HTMX_0002,
                    severity=DiagnosticSeverity.ERROR,
                    title="select_oob uses non-#id selectors",
                    explanation=(
                        f"{file_path} has hx-select-oob / select_oob token(s) that "
                        f"are not simple #id selectors ({tokens}). Hedron conflict "
                        "detection only understands #id lists."
                    ),
                    remediation=(
                        "Prefer comma-separated #id targets for select_oob so "
                        "hedron check can detect OobUpdate conflicts."
                    ),
                    context={"path": file_path, "unparsed": sorted(unparsed)},
                )
            )
    return diags


_SKIP_SCAN_DIRS = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "venv",
        "node_modules",
        "dist",
        "build",
        "site",
        "site-packages",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
    }
)
_IMPORT_ROOT_RE = re.compile(
    r"(?m)^\s*(?:from|import)\s+([A-Za-z_][\w.]*)",
)


def _path_is_skipped(path: Path, *, base: Path) -> bool:
    try:
        parts = path.resolve().relative_to(base.resolve()).parts
    except ValueError:
        parts = path.parts
    return any(part in _SKIP_SCAN_DIRS for part in parts)


def _iter_project_py_files(base: Path) -> list[Path]:
    if not base.exists():
        return []
    files: list[Path] = []
    for path in base.rglob("*.py"):
        if _path_is_skipped(path, base=base):
            continue
        files.append(path)
    return files


def _app_source_paths(app_path: str | None) -> list[Path]:
    """Return source files for a loaded ``--app`` module/package."""
    if not app_path or ":" not in app_path:
        return []
    module_name = app_path.split(":", 1)[0]
    module = sys.modules.get(module_name)
    if module is None:
        return []
    file_name = getattr(module, "__file__", None)
    if not file_name:
        return []
    path = Path(file_name).resolve()
    paths = [path]
    package_dir = path.parent if path.name == "__init__.py" else None
    if package_dir is not None and package_dir.is_dir():
        paths.extend(sorted(package_dir.rglob("*.py")))
    return paths


def _files_import_any(paths: list[Path], roots: frozenset[str]) -> bool:
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for match in _IMPORT_ROOT_RE.finditer(text):
            top = match.group(1).split(".", 1)[0]
            if top in roots:
                return True
    return False


def _manifest_mentions(base: Path, tokens: frozenset[str]) -> bool:
    lowered = tuple(token.lower() for token in tokens)
    for name in ("pyproject.toml", "requirements.txt", "requirements.in", "Pipfile"):
        path = base / name
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8").lower()
        except OSError:
            continue
        if any(token in text for token in lowered):
            return True
    return False


def _registry_has_chart_surface() -> bool:
    markers = ("chart", "plotly", "altair", "vega")
    for meta in get_registry().components():
        blob = f"{meta.distribution} {meta.name} {meta.logical_id}".lower()
        if any(marker in blob for marker in markers):
            return True
    return False


def _compat_surface_active(
    base: Path,
    *,
    app: str | None,
    module_roots: frozenset[str],
    package_tokens: frozenset[str],
    registry_active: bool = False,
) -> bool:
    """True when the project/app references a compatibility surface (not ambient installs)."""
    if registry_active:
        return True
    paths = [*_iter_project_py_files(base), *_app_source_paths(app)]
    if _files_import_any(paths, module_roots):
        return True
    return _manifest_mentions(base, module_roots | package_tokens)


def _compat_info_diagnostics(
    *,
    base: Path,
    app: str | None,
    all_compat: bool,
) -> list[Any]:
    """Evergreen informational findings; adapter/extra notices are project-scoped (#54)."""
    from hedron_core import DiagnosticSeverity
    from hedron_core.diagnostics import make_diagnostic

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
            title="0.19 compatibility baseline is active",
            explanation=(
                "Phase 0.19 classifies the public API and accessibility contracts. "
                "See docs/api/STABILITY.md for Supported vs experimental surfaces."
            ),
            remediation="See docs/api/STABILITY.md and docs/guides/upgrade.md.",
        ),
    ]
    django_active = all_compat or _compat_surface_active(
        base,
        app=app,
        module_roots=frozenset({"django", "hedron_django"}),
        package_tokens=frozenset({"hedron-django"}),
    )
    if django_active:
        info_diags.append(
            make_diagnostic(
                "HED-COMPAT-0002",
                severity=DiagnosticSeverity.INFORMATION,
                title="Django Supported floor is 5.2 LTS",
                explanation="hedron-django requires Django >=5.2,<6 for Supported adapter claims.",
                remediation="Upgrade Django to the 5.2 LTS line before production adapter use.",
            )
        )
    charts_active = all_compat or _compat_surface_active(
        base,
        app=app,
        module_roots=frozenset({"hedron_charts", "plotly", "altair"}),
        package_tokens=frozenset({"hedron-charts", "hedron[charts]"}),
        registry_active=_registry_has_chart_surface(),
    )
    if charts_active:
        info_diags.append(
            make_diagnostic(
                "HED-COMPAT-0003",
                severity=DiagnosticSeverity.INFORMATION,
                title="Interactive Plotly/Altair runtimes are experimental",
                explanation=(
                    "Full Plotly/Vega interactive hosts remain experimental until offline pins "
                    "and browser evidence promote them; prefer Matplotlib static SVG for stable "
                    "dashboards."
                ),
                remediation="See docs/api/STABILITY.md and docs/api/CHART.md.",
            )
        )
    return info_diags


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
    # CSS discovery compile checks
    from hedron_core import HedronError, compile_css
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

    diags.extend(_check_htmx_region_mismatches(base))
    diags.extend(_check_select_oob_conflicts(base))

    # Security / a11y / compatibility-boundary informational findings (excluded from exit code).
    # Adapter/extra COMPAT notices are scoped to the project under check unless --all-compat (#54).
    info_diags = _compat_info_diagnostics(
        base=base,
        app=getattr(args, "app", None),
        all_compat=bool(getattr(args, "all_compat", False)),
    )

    inventory_summary: JsonObject | None = None
    hdj_reports: list[JsonObject] = []

    # Optional HDJ production inventory / CSP mismatch summary (hedron-jinja).
    try:
        from hedron_jinja import build_production_inventory, reconcile_csp
        from hedron_jinja.source import inferred_capabilities, parse_hdj_source
    except ImportError:
        pass
    else:
        reports: list[JsonObject] = []
        caps: set[str] = set()
        mismatches: list[str] = []
        csp_policy: str | None = None
        try:
            from hedron.security.policy import SecurityPolicy

            csp_policy = SecurityPolicy.from_name("standard").content_security_policy
        except Exception:  # noqa: BLE001
            csp_policy = None
        for root in settings.resolved_roots(base=base) or [base]:
            root = Path(root).resolve()
            if not root.exists():
                continue
            for path in sorted(root.rglob("*.hdj")):
                if any(
                    part.startswith(".")
                    or part in {"node_modules", ".venv", "dist", "site-packages"}
                    for part in path.parts
                ):
                    continue
                try:
                    rel = str(path.relative_to(base if path.is_relative_to(base) else root))
                    text = path.read_text(encoding="utf-8")
                    parsed = parse_hdj_source(rel, text)
                    inferred = set(inferred_capabilities(parsed))
                    declared = set(parsed.declaration.requires)
                    required = sorted(inferred | declared)
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
                            csp_policy,
                            required_capabilities=required,
                            source_name=rel,
                        )
                    )
                except Exception as exc:  # noqa: BLE001
                    reports.append({"name": str(path), "error": str(exc)})
        hdj_reports = reports
        inv = build_production_inventory(
            template_reports=reports,
            capabilities=sorted(caps),
        )
        if mismatches:
            diags.append(
                make_diagnostic(
                    "HED-HDJ-0110",
                    severity=DiagnosticSeverity.WARNING,
                    title="HDJ CSP capability mismatches",
                    explanation="; ".join(mismatches[:5]),
                    remediation="Align SecurityPolicy CSP with declared HDJ capabilities.",
                )
            )
        elif reports:
            info_diags.append(
                make_diagnostic(
                    "HED-HDJ-0100",
                    severity=DiagnosticSeverity.INFORMATION,
                    title="HDJ production inventory",
                    explanation=(
                        f"Scanned {len(reports)} template(s); "
                        f"capabilities={sorted(caps) or ['(none)']}."
                    ),
                    remediation="See Explorer /inventory and docs/api for HDJ CSP reconciliation.",
                )
            )
        inventory_summary = cast(
            JsonObject,
            {
                "templates": len(reports),
                "capabilities": sorted(caps),
                "csp_mismatches": mismatches,
                "inventory": inv.as_dict(),
            },
        )

    all_diags = [*diags, *info_diags]

    threshold = DiagnosticSeverity(args.severity)
    fmt = args.format
    if fmt == "json":
        print(json.dumps(diagnostics_to_json(all_diags), indent=2))
        if inventory_summary is not None:
            print(json.dumps({"hdj_inventory": inventory_summary}, indent=2))
    elif fmt == "sarif":
        print(json.dumps(diagnostics_to_sarif(all_diags), indent=2))
    else:
        text = diagnostics_to_text(all_diags)
        print(text or "No diagnostics.")
        if inventory_summary is not None and hdj_reports:
            print(f"HDJ inventory: {json.dumps(inventory_summary, indent=2)}")
    # Exit on real findings only — evergreen INFORMATION never fails the gate.
    return 1 if meets_severity_threshold(diags, threshold) else 0


def _cmd_graph(args: argparse.Namespace) -> int:
    _load_app(args.app)
    base = Path(getattr(args, "project", None) or Path.cwd()).resolve()
    _apply_project_discovery(base)
    registry = get_registry()
    nodes: list[JsonObject] = []
    edges: list[JsonObject] = []
    for c in registry.components():
        nodes.append({"id": c.logical_id, "name": c.name, "kind": "component"})
        for dep in c.browser_modules:
            edges.append({"from": c.logical_id, "to": dep, "kind": "browser_module"})
        if c.styles_path:
            edges.append({"from": c.logical_id, "to": c.styles_path, "kind": "styles"})
    inverse: dict[str, list[str]] = {}
    for edge in edges:
        inverse.setdefault(str(edge["to"]), []).append(str(edge["from"]))
    payload: JsonObject = cast(
        JsonObject,
        {"nodes": nodes, "edges": edges, "inverse_consumers": inverse},
    )
    print(json.dumps(payload, indent=2))
    return 0


def _cmd_conformance(args: argparse.Namespace) -> int:
    """Run the published language-neutral conformance kit (phase 0.14)."""
    try:
        from hedron_conformance.cli import main as conformance_main
    except ImportError:
        print(
            "hedron-conformance is not installed. Install with: pip install 'hedron[conformance]'",
            file=sys.stderr,
        )
        return 2
    argv = ["run"]
    if args.json:
        argv.append("--json")
    return int(conformance_main(argv))


def _cmd_accel_status(args: argparse.Namespace) -> int:
    """Report optional native acceleration status."""
    try:
        from hedron_native import __version__ as native_version
        from hedron_native import native_available, native_disabled_by_env
    except ImportError:
        print("hedron-native: not installed (pure-Python serializer active)")
        return 0
    if native_disabled_by_env():
        print(
            f"hedron-native {native_version}: disabled "
            "(HEDRON_NATIVE_DISABLE; pure-Python serializer active)"
        )
        return 0
    status = "loaded" if native_available() else "installed (fallback pure-Python)"
    print(f"hedron-native {native_version}: {status}")
    return 0


def _cmd_audit_components(args: argparse.Namespace) -> int:
    _load_app(args.app)
    base = Path(getattr(args, "project", None) or Path.cwd()).resolve()
    _apply_project_discovery(base)
    from hedron_core.plugins import get_diagnostic_owners, get_explorer_panels

    registry = get_registry()
    rows: list[JsonObject] = []
    for c in registry.components():
        rows.append(
            {
                "logical_id": c.logical_id,
                "name": c.name,
                "distribution": c.distribution,
                "module": c.module,
                "capabilities": {
                    "styles": bool(c.styles_path),
                    "browser_js": bool(c.browser_modules),
                    "assets": bool(c.asset_roots),
                },
            }
        )
    plugin_rows: list[JsonObject] = []
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
                    plugin_rows.append(cast(JsonObject, cast(PluginMetaDict, meta.to_dict())))
                else:
                    plugin_rows.append({"name": ep.name, "version": "unknown"})
            except Exception as exc:  # noqa: BLE001
                plugin_rows.append({"name": ep.name, "error": str(exc)})
    except Exception:  # noqa: BLE001
        plugin_rows = []
    payload: JsonObject = cast(
        JsonObject,
        {
            "components": rows,
            "plugins": plugin_rows,
            "explorer_panels": [p.to_dict() for p in get_explorer_panels()],
            "diagnostic_owners": dict(get_diagnostic_owners()),
        },
    )
    print(json.dumps(payload, indent=2))
    return 0


def _cmd_dev(args: argparse.Namespace) -> int:
    from hedron.build import run_build
    from hedron.config import load_hedron_settings

    base = Path(args.project or Path.cwd()).resolve()
    settings = load_hedron_settings(base)
    roots = list(settings.resolved_roots(base=base))
    watch_exts = {
        ".css",
        ".html",
        ".jinja",
        ".jinja2",
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
                except Exception as exc:  # noqa: BLE001
                    print(f"build failed (previous output retained): {exc}", file=sys.stderr)
    except KeyboardInterrupt:
        print("stopped", file=sys.stderr)
        return 0


def _cmd_run_app(args: argparse.Namespace) -> int:
    """Run locally, or delegate to the optional Workbench pre-import launcher."""
    import os

    target = str(args.target or args.app or "").strip()
    if not target or ":" not in target:
        print("hedron run requires module:attribute", file=sys.stderr)
        return 2
    workbench_runtime = bool(str(os.environ.get("RS_SERVER_URL") or "").strip())
    if args.workbench or workbench_runtime:
        try:
            from hedron_workbench.config import (
                WorkbenchConfig,
                WorkbenchMode,
                WorkbenchTopology,
            )
            from hedron_workbench.runner import run_target
        except ImportError:
            print(
                "Posit Workbench runtime detected but hedron-workbench is not installed; "
                "install hedron[workbench]",
                file=sys.stderr,
            )
            return 2
        config = WorkbenchConfig(
            mode=WorkbenchMode.parse(args.workbench_mode),
            host=args.host,
            port=args.port,
            mount=args.mount,
            public_base_url=args.public_base_url,
            forwarded_allow_ips=args.forwarded_allow_ips,
            allow_external_bind=args.allow_external_bind,
            reload=args.reload,
            workers=args.workers,
            debug=args.debug,
            factory=args.factory,
            app_target=target,
            topology=WorkbenchTopology.parse(args.topology),
        )
        run_target(target, config=config)
        return 0

    import uvicorn

    uvicorn.run(
        target,
        host=args.host or "127.0.0.1",
        port=args.port or 8000,
        reload=args.reload,
        workers=args.workers,
        factory=args.factory,
        log_level="debug" if args.debug else "info",
    )
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

    inspect_p = sub.add_parser(
        "inspect",
        help="Explain a component's styles, dependencies, and accessibility contract",
    )
    inspect_p.add_argument("component", help="Component name or logical id")
    inspect_p.set_defaults(func=_cmd_inspect)

    eject_p = sub.add_parser(
        "eject",
        help="Eject accessibility_contract.json and editable local CSS overrides",
    )
    eject_p.add_argument("component", help="Component name or logical id")
    eject_p.add_argument("--out", help="Output directory")
    eject_p.add_argument("--force", action="store_true")
    eject_p.set_defaults(func=_cmd_eject)

    build_p = sub.add_parser("build", help="Compile CSS/assets into a build manifest")
    build_p.add_argument("--project", default=None)
    build_p.add_argument("--dev", action="store_true", help="Use readable development names")
    build_p.set_defaults(func=_cmd_build)

    new_p = sub.add_parser("new", help="Scaffold a new Hedron application")
    new_p.add_argument("name", help="Project name")
    new_p.add_argument("--path", default=None, help="Destination directory")
    new_p.add_argument("--force", action="store_true")
    new_p.add_argument(
        "--flask",
        action="store_true",
        help="Scaffold a Flask + hedron-flask app (no FastAPI dependency)",
    )
    new_p.add_argument(
        "--django",
        action="store_true",
        help="Scaffold a Django + hedron-django app (no FastAPI dependency)",
    )
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
    check_p.add_argument(
        "--all-compat",
        action="store_true",
        help=(
            "Include global adapter/extra compatibility notices even when those "
            "integrations are not detected in the project under check"
        ),
    )
    check_p.set_defaults(func=_cmd_check)

    graph_p = sub.add_parser("graph", help="Component dependency graph")
    graph_p.set_defaults(func=_cmd_graph)

    audit_p = sub.add_parser("audit-components", help="Capability and package audit")
    audit_p.set_defaults(func=_cmd_audit_components)

    conf_p = sub.add_parser(
        "conformance",
        help="Run the published language-neutral conformance kit (requires hedron[conformance])",
    )
    conf_p.add_argument("--json", action="store_true", help="Emit JSON report")
    conf_p.set_defaults(func=_cmd_conformance)

    accel_p = sub.add_parser(
        "accel-status",
        help="Report optional hedron-native acceleration status",
    )
    accel_p.set_defaults(func=_cmd_accel_status)

    dev_p = sub.add_parser("dev", help="Watch Python/Jinja/CSS/assets and rebuild atomically")
    dev_p.add_argument("--project", default=None)
    dev_p.add_argument("--interval", type=float, default=0.5)
    dev_p.add_argument("--once", action="store_true", help="Build once and exit")
    dev_p.set_defaults(func=_cmd_dev)

    run_p = sub.add_parser(
        "run",
        help="Run an ASGI app; auto-use hedron-workbench inside Posit Workbench",
    )
    run_p.add_argument("target", nargs="?", help="module:app or module:factory")
    run_p.add_argument("--factory", action="store_true")
    run_p.add_argument("--host")
    run_p.add_argument("--port", type=int)
    run_p.add_argument("--reload", action="store_true")
    run_p.add_argument("--workers", type=int, default=1)
    run_p.add_argument("--debug", action="store_true")
    run_p.add_argument("--workbench", action="store_true")
    run_p.add_argument("--workbench-mode", choices=("auto", "on", "off"), default="auto")
    run_p.add_argument("--mount")
    run_p.add_argument("--public-base-url")
    run_p.add_argument("--forwarded-allow-ips")
    run_p.add_argument("--allow-external-bind", action="store_true")
    run_p.add_argument(
        "--topology",
        choices=(
            "auto",
            "local",
            "launcher-local",
            "launcher-kubernetes",
            "launcher-slurm",
            "reverse-proxy",
        ),
        default="auto",
    )
    run_p.set_defaults(func=_cmd_run_app)

    migrate_p = sub.add_parser(
        "migrate",
        help="Reviewable framework migration assistants (RFC-0061)",
    )
    migrate_sub = migrate_p.add_subparsers(dest="migrate_command", required=True)
    from hedron.migrate.cli import build_streamlit_parser

    build_streamlit_parser(migrate_sub)

    args = parser.parse_args(argv)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
