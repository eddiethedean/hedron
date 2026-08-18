"""CLI command: project diagnostics and AST scanners."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any, cast

from hedron.cli.discovery import _apply_project_discovery, _load_app
from hedron_core.registry import get_registry
from hedron_core.typing_aliases import JsonObject


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


def _check_043_handles(base: Path) -> list[Any]:
    """IH-DX-006: duplicate mounts, stale paths, foreign handles, missing fallback, fan-out."""
    from hedron_core import DiagnosticSeverity
    from hedron_core.codes import (
        HED_CMD_0002,
        HED_UPDATE_0003,
        HED_UPDATE_0004,
        HED_VIEW_0002,
    )
    from hedron_core.diagnostics import make_diagnostic
    from hedron_core.updates import MAX_REFRESH_TARGETS, list_handle_descriptors

    diags: list[Any] = []
    refreshable_names: dict[str, str] = {}
    command_without_fallback: list[str] = []
    for path in _iter_project_py_files(base):
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for deco in node.decorator_list:
                    name = _decorator_attr(deco)
                    if name == "refreshable":
                        owner = refreshable_names.get(node.name)
                        if owner and owner != str(path):
                            diags.append(
                                make_diagnostic(
                                    HED_VIEW_0002,
                                    severity=DiagnosticSeverity.ERROR,
                                    title="Duplicate refreshable name",
                                    explanation=(
                                        f"{node.name} is registered in both {owner} and {path}."
                                    ),
                                    remediation="Use distinct names or explicit key=.",
                                )
                            )
                        refreshable_names[node.name] = str(path)
                    if name == "command" and not _decorator_has_kw(deco, "fallback"):
                        command_without_fallback.append(f"{path}:{node.name}")
            if isinstance(node, ast.Call):
                func = node.func
                if (
                    isinstance(func, ast.Name)
                    and func.id == "refresh"
                    and len(node.args) > MAX_REFRESH_TARGETS
                ):
                    diags.append(
                        make_diagnostic(
                            HED_UPDATE_0004,
                            severity=DiagnosticSeverity.ERROR,
                            title="Unbounded refresh fan-out",
                            explanation=(
                                f"{path} calls refresh() with {len(node.args)} targets; "
                                f"max is {MAX_REFRESH_TARGETS}."
                            ),
                            remediation="Coalesce or reduce fan-out; refresh is not atomic.",
                        )
                    )
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                value = node.value
                if "/_hedron/views/" in value or "/_hedron/commands/" in value:
                    registered = {item.path for item in list_handle_descriptors()}
                    if (
                        registered
                        and value not in registered
                        and not any(value.startswith(path_value) for path_value in registered)
                    ):
                        diags.append(
                            make_diagnostic(
                                HED_UPDATE_0003,
                                severity=DiagnosticSeverity.WARNING,
                                title="Copied stale handle path",
                                explanation=f"{path} embeds generated path {value!r}.",
                                remediation=(
                                    "Use handle.path / handle.bind(...) instead of copied URLs."
                                ),
                            )
                        )
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "fragment"
            ):
                diags.append(
                    make_diagnostic(
                        "HED-HTMX-0001",
                        severity=DiagnosticSeverity.INFORMATION,
                        title="Consider migrating @app.fragment to @app.refreshable",
                        explanation=(
                            f"{path} still uses @app.fragment. 0.43 prefers "
                            "@app.refreshable handles."
                        ),
                        remediation=(
                            "See docs/acceptance/upgrade-fixtures-043.md for a one-view migration."
                        ),
                    )
                )
    for item in command_without_fallback:
        diags.append(
            make_diagnostic(
                HED_CMD_0002,
                severity=DiagnosticSeverity.WARNING,
                title="Command missing fallback for ordinary HTTP",
                explanation=(
                    f"{item} has no fallback=; HTMX refresh cannot be the only success path."
                ),
                remediation="Pass fallback= to @app.command or handle.button(fallback=...).",
            )
        )
    return diags


def _check_044_type_authoring(base: Path) -> list[Any]:
    """Static AST inspection never imports the target project."""
    from hedron_core import DiagnosticSeverity
    from hedron_core.codes import HED_TYPE_0004
    from hedron_core.diagnostics import make_diagnostic
    from hedron_core.type_schema import TYPE_SCHEMA_NAMESPACE, type_schema_from_descriptor
    from hedron_core.updates import descriptor_fingerprint, list_handle_descriptors

    diags: list[Any] = []
    for path in _iter_project_py_files(base):
        try:
            source = path.read_text(encoding="utf-8")
            ast.parse(source, filename=str(path))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
    for descriptor in list_handle_descriptors():
        schema = type_schema_from_descriptor(descriptor)
        if schema is None:
            continue
        if (
            schema.descriptor_fingerprint
            and schema.descriptor_fingerprint != descriptor_fingerprint(descriptor)
        ):
            diags.append(
                make_diagnostic(
                    HED_TYPE_0004,
                    severity=DiagnosticSeverity.ERROR,
                    title="TypeSchema fingerprint mismatch",
                    explanation=(
                        f"Handle {descriptor.logical_id!r} has stale "
                        f"{TYPE_SCHEMA_NAMESPACE} metadata."
                    ),
                    remediation="Rebuild so TypeSchema matches the 0.43 descriptor fingerprint.",
                )
            )
    return diags


def _decorator_attr(node: ast.AST) -> str | None:
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        return node.func.attr
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node, ast.Name):
        return node.id
    return None


def _decorator_has_kw(node: ast.AST, name: str) -> bool:
    if not isinstance(node, ast.Call):
        return False
    return any(kw.arg == name for kw in node.keywords)


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

    app = _load_app(args.app)
    base = Path(args.project or Path.cwd()).resolve()
    settings = _apply_project_discovery(base)
    diags = []
    explorer_diff: JsonObject | None = None
    try:
        from hedron_explorer.services.diff import explorer_diff_report
        from hedron_explorer.services.health import package_health

        package_health()
        explorer_diff = cast(JsonObject, explorer_diff_report(app))
    except ImportError:
        print("hedron-explorer: skipped (not installed)", file=sys.stderr)
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
    diags.extend(_check_043_handles(base))
    diags.extend(_check_044_type_authoring(base))

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
        if explorer_diff is not None:
            print(json.dumps({"explorer_diff": explorer_diff}, indent=2))
    elif fmt == "sarif":
        print(json.dumps(diagnostics_to_sarif(all_diags), indent=2))
    else:
        text = diagnostics_to_text(all_diags)
        print(text or "No diagnostics.")
        if inventory_summary is not None and hdj_reports:
            print(f"HDJ inventory: {json.dumps(inventory_summary, indent=2)}")
        if explorer_diff is not None:
            print("Explorer diff:")
            print(json.dumps(explorer_diff, indent=2))
    # Exit on real findings only — evergreen INFORMATION never fails the gate.
    return 1 if meets_severity_threshold(diags, threshold) else 0
