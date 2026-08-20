"""CLI commands: theme token/contrast checks and zero-application-CSS audits."""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Iterable, Sequence
from pathlib import Path

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
    run_visual_conformance,
)

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


def _cmd_theme_check(args: argparse.Namespace) -> int:
    """Validate theme tokens, element compatibility, and contrast basics."""
    themes = _themes_for(getattr(args, "theme", None))
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


def _cmd_style_check(args: argparse.Namespace) -> int:
    """Audit a path for application-authored CSS (``--zero-app-css``)."""
    target = getattr(args, "zero_app_css", None)
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
