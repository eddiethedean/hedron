"""CLI commands: theme token/contrast checks and zero-application-CSS audits."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Protocol

from hedron_core.codes import HED_CSS_APPLICATION_AUTHORED, HED_THEME_MISSING_TOKEN
from hedron_core.diagnostics import (
    Diagnostic,
    DiagnosticSeverity,
    diagnostics_to_json,
    diagnostics_to_text,
    make_diagnostic,
    meets_severity_threshold,
    normalize_severity_alias,
)
from hedron_core.theme import (
    REQUIRED_A11Y_TOKENS,
    Theme,
    builtin_themes,
    contrast_diagnostics,
    default_theme,
    run_visual_conformance,
)
from hedron_core.theme_contract import (
    build_state_matrix,
    component_contract_manifest,
    element_metadata_manifest,
    export_theme,
    inspect_theme_css,
    theme_contract_report,
)
from hedron_core.theme_platform import ThemeSpec
from hedron_core.typing_aliases import is_string_mapping


class _ThemeArgs(Protocol):
    accessibility_mode: list[str]
    component: list[str]
    format: str
    mode: list[str]
    output: str | None
    profile: str
    severity: str
    spec: str | None
    stylesheet: str | None
    theme: list[str] | None
    theme_name: str | None
    viewport: list[str]
    zero_app_css: str | None


# Directories that never hold hand-authored application presentation.
_SKIP_DIRS = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".hedron",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
        "site-packages",
        "venv",
    }
)
_STYLESHEET_SUFFIXES = frozenset({".css", ".scss", ".sass", ".less", ".styl"})
_MARKUP_SUFFIXES = frozenset({".html", ".htm", ".jinja", ".jinja2", ".j2", ".hdj"})
_STYLE_BLOCK = re.compile(r"<style\b", re.IGNORECASE)
_STYLE_ATTR = re.compile(r"\sstyle\s*=\s*[\"']", re.IGNORECASE)


def _themes_for(names: Sequence[str] | None) -> list[Theme]:
    available = {theme.name: theme for theme in builtin_themes()}
    if not names:
        return list(available.values())
    available["default"] = default_theme()
    selected: list[Theme] = []
    for name in names:
        theme = available.get(name)
        if theme is None:
            known = ", ".join(sorted(available))
            raise SystemExit(f"hedron theme check: unknown theme {name!r} (known: {known})")
        selected.append(theme)
    return selected


def _token_diagnostics(theme: Theme) -> list[Diagnostic]:
    missing = [token for token in REQUIRED_A11Y_TOKENS if token not in theme.tokens]
    if not missing:
        return []
    return [
        make_diagnostic(
            HED_THEME_MISSING_TOKEN,
            severity=DiagnosticSeverity.ERROR,
            title="Theme missing required accessibility tokens",
            explanation=f"{theme.name} is missing: {', '.join(missing)}.",
            remediation="Provide every token listed in REQUIRED_A11Y_TOKENS.",
        )
    ]


def _cmd_theme_check(args: _ThemeArgs) -> int:
    """Validate theme tokens, element compatibility, and contrast basics."""
    themes = _themes_for(args.theme)
    diagnostics: list[Diagnostic] = []
    for theme in themes:
        diagnostics.extend(_token_diagnostics(theme))
        diagnostics.extend(run_visual_conformance(theme))
        diagnostics.extend(contrast_diagnostics(theme))
    threshold = normalize_severity_alias(args.severity)
    if args.format == "json":
        print(
            json.dumps(
                {
                    "themes": [theme.name for theme in themes],
                    "diagnostics": diagnostics_to_json(diagnostics),
                },
                indent=2,
            )
        )
    else:
        checked = ", ".join(theme.name for theme in themes)
        print(f"Checked themes: {checked}")
        print(diagnostics_to_text(diagnostics) or "No diagnostics.")
    return 1 if meets_severity_threshold(diagnostics, threshold) else 0


def _theme_input(args: _ThemeArgs) -> Theme | ThemeSpec:
    spec_path = args.spec
    if spec_path:
        try:
            payload = json.loads(Path(spec_path).read_text(encoding="utf-8"))
            if not is_string_mapping(payload):
                raise ValueError("theme spec JSON must contain an object")
            return ThemeSpec.from_dict(payload)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise SystemExit(f"hedron theme: invalid spec {spec_path}: {exc}") from exc
    name = args.theme_name or "folio"
    available = {theme.name: theme for theme in builtin_themes()}
    available["default"] = default_theme()
    if name not in available:
        raise SystemExit(f"hedron theme: unknown theme {name!r}")
    return available[name]


def _write_or_print(value: str, output: str | None) -> None:
    if output:
        _ignored = Path(output).write_text(value, encoding="utf-8")
    else:
        print(value, end="")


def _cmd_theme_export(args: _ThemeArgs) -> int:
    exported = export_theme(_theme_input(args), profile=args.profile)
    if args.format == "css":
        value = exported.css
    elif args.format == "json":
        value = exported.json
    else:
        value = json.dumps(exported.to_dict(), indent=2, sort_keys=True) + "\n"
    _write_or_print(value, args.output)
    return 0


def _cmd_theme_manifest(args: _ThemeArgs) -> int:
    value = json.dumps(component_contract_manifest(), indent=2, sort_keys=True) + "\n"
    _write_or_print(value, args.output)
    return 0


def _cmd_theme_metadata(args: _ThemeArgs) -> int:
    value = json.dumps(element_metadata_manifest(), indent=2, sort_keys=True) + "\n"
    _write_or_print(value, args.output)
    return 0


def _cmd_theme_matrix(args: _ThemeArgs) -> int:
    matrix = build_state_matrix(
        components=args.component or None,
        viewports=args.viewport or ("320", "390", "1440"),
        modes=args.mode or ("light", "dark"),
        accessibility_modes=args.accessibility_mode
        or (
            "none",
            "forced-colors",
            "high-contrast",
            "reduced-motion",
            "reduced-transparency",
            "print",
        ),
    )
    value = json.dumps(matrix.to_dict(), indent=2, sort_keys=True) + "\n"
    _write_or_print(value, args.output)
    return 0


def _cmd_theme_contract(args: _ThemeArgs) -> int:
    theme = _theme_input(args)
    stylesheet = Path(args.stylesheet).read_text(encoding="utf-8") if args.stylesheet else None
    value = (
        json.dumps(theme_contract_report(theme, css=stylesheet), indent=2, sort_keys=True) + "\n"
    )
    _write_or_print(value, args.output)
    return 0


def _cmd_theme_inspect(args: _ThemeArgs) -> int:
    if args.stylesheet is None:
        raise SystemExit("hedron theme inspect requires --stylesheet")
    try:
        stylesheet = Path(args.stylesheet).read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"hedron theme inspect: cannot read {args.stylesheet}: {exc}") from exc
    value = json.dumps(inspect_theme_css(stylesheet), indent=2, sort_keys=True) + "\n"
    _write_or_print(value, args.output)
    return 0


def _iter_candidate_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        yield root
        return
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        yield path


def application_css_findings(root: Path) -> list[Diagnostic]:
    """Return one diagnostic per hand-authored stylesheet or inline style block."""
    findings: list[Diagnostic] = []
    for path in _iter_candidate_files(root):
        relative = path.relative_to(root) if root.is_dir() else Path(path.name)
        suffix = path.suffix.lower()
        if suffix in _STYLESHEET_SUFFIXES:
            findings.append(
                make_diagnostic(
                    HED_CSS_APPLICATION_AUTHORED,
                    severity=DiagnosticSeverity.ERROR,
                    title="Application stylesheet found",
                    explanation=f"{relative} is an application-authored stylesheet.",
                    remediation=(
                        "Move the intent into Theme tokens/design-system fields and "
                        "Hedron built-ins; applications on this path author no CSS."
                    ),
                )
            )
            continue
        if suffix not in _MARKUP_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if _STYLE_BLOCK.search(text):
            findings.append(
                make_diagnostic(
                    HED_CSS_APPLICATION_AUTHORED,
                    severity=DiagnosticSeverity.ERROR,
                    title="Inline <style> block found",
                    explanation=f"{relative} contains a <style> block.",
                    remediation="Replace the block with Theme tokens and built-in components.",
                )
            )
        if _STYLE_ATTR.search(text):
            findings.append(
                make_diagnostic(
                    HED_CSS_APPLICATION_AUTHORED,
                    severity=DiagnosticSeverity.ERROR,
                    title="Inline style attribute found",
                    explanation=f"{relative} contains a style= attribute.",
                    remediation=(
                        "Use layout built-ins; only Hedron layout custom properties "
                        "are permitted on style=."
                    ),
                )
            )
    return findings


def _cmd_style_check(args: _ThemeArgs) -> int:
    """Audit a path for application-authored CSS (``--zero-app-css``)."""
    target = args.zero_app_css
    if not target:
        raise SystemExit("hedron style check requires --zero-app-css PATH")
    root = Path(target).resolve()
    if not root.exists():
        raise SystemExit(f"hedron style check: path not found: {target}")
    findings = application_css_findings(root)
    if args.format == "json":
        print(
            json.dumps(
                {
                    "path": str(root),
                    "zero_app_css": not findings,
                    "diagnostics": diagnostics_to_json(findings),
                },
                indent=2,
            )
        )
    elif findings:
        print(diagnostics_to_text(findings))
    else:
        print(f"ok: no application-authored CSS under {root}")
    return 1 if findings else 0


cmd_style_check = _cmd_style_check
cmd_theme_check = _cmd_theme_check
cmd_theme_contract = _cmd_theme_contract
cmd_theme_export = _cmd_theme_export
cmd_theme_inspect = _cmd_theme_inspect
cmd_theme_manifest = _cmd_theme_manifest
cmd_theme_matrix = _cmd_theme_matrix
cmd_theme_metadata = _cmd_theme_metadata
