"""CLI handlers for Edron migration commands."""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path
from typing import Any

from edron.migrate.analyze import analyze_source
from edron.migrate.codemod import codemod_file
from edron.migrate.generate import generate_project
from edron.migrate.report import format_report
from hedron.migrate.findings import plan_to_diagnostics
from hedron_core.diagnostics import DiagnosticSeverity, meets_severity_threshold


def build_migrate_parser(subparsers: Any) -> None:
    migrate = subparsers.add_parser("migrate", help="migrate a Streamlit app to Edron")
    commands = migrate.add_subparsers(dest="migrate_command")
    streamlit = commands.add_parser("streamlit", help="analyze and generate an Edron project")
    streamlit.add_argument("source")
    streamlit.add_argument("--out", default=None)
    streamlit.add_argument("--project-root", default=None)
    streamlit.add_argument("--analyze-only", action="store_true")
    streamlit.add_argument("--format", choices=("text", "json", "sarif"), default="text")
    streamlit.add_argument(
        "--python-version", choices=("3.10", "3.11", "3.12", "3.13", "3.14"), default="3.12"
    )
    streamlit.add_argument(
        "--fail-on", choices=("information", "warning", "error"), default="error"
    )
    streamlit.set_defaults(func=run_migrate_streamlit_args)
    codemod = commands.add_parser("codemod", help="preview or write safe Edron syntax codemods")
    codemod.add_argument("source")
    codemod.add_argument("--out", default=None)
    codemod.add_argument("--preview", action="store_true")
    codemod.add_argument("--format", choices=("text", "json"), default="text")
    codemod.set_defaults(func=run_codemod_args)


def run_migrate_streamlit_args(args: argparse.Namespace) -> int:
    return run_migrate_streamlit(
        source=Path(args.source),
        out=Path(args.out) if args.out else None,
        project_root=Path(args.project_root) if args.project_root else None,
        analyze_only=args.analyze_only,
        fmt=args.format,
        python_version=args.python_version,
        fail_on=args.fail_on,
    )


def run_migrate_streamlit(
    *,
    source: Path,
    out: Path | None = None,
    project_root: Path | None = None,
    analyze_only: bool = False,
    fmt: str = "text",
    python_version: str = "3.12",
    fail_on: str = "error",
) -> int:
    if not analyze_only and out is None:
        print("--out is required unless --analyze-only is set", file=sys.stderr)
        return 1
    plan = analyze_source(source, project_root=project_root, python_version=python_version)
    diagnostics = plan_to_diagnostics(plan)
    if plan.tool_errors:
        sys.stdout.write(format_report(plan, fmt=fmt))
        return 1
    generated: dict[str, str] = {}
    if not analyze_only:
        try:
            generated = generate_project(plan, out) if out is not None else {}
        except (OSError, RuntimeError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
    sys.stdout.write(format_report(plan, fmt=fmt, generated_files=generated or None))
    if meets_severity_threshold(diagnostics, DiagnosticSeverity(fail_on)):
        print("REVIEW REQUIRED", file=sys.stderr)
        return 2
    return 0


def run_codemod_args(args: argparse.Namespace) -> int:
    source = Path(args.source)
    result = codemod_file(
        source, Path(args.out) if args.out and not args.preview else None, preview=args.preview
    )
    payload = {
        "source": str(source),
        "changed": result.changed,
        "replacements": [
            {
                "old": replacement.old,
                "new": replacement.new,
                "line": replacement.line,
                "column": replacement.column,
            }
            for replacement in result.replacements
        ],
        "diagnostics": list(result.diagnostics),
    }
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"Codemod: {'changed' if result.changed else 'no changes'}")
        for replacement in result.replacements:
            print(
                f"- {replacement.old} -> {replacement.new} "
                f"({replacement.line}:{replacement.column})"
            )
        if args.preview and result.changed:
            original = source.read_text(encoding="utf-8")
            print(
                "".join(
                    difflib.unified_diff(
                        original.splitlines(keepends=True),
                        result.source.splitlines(keepends=True),
                        fromfile=str(source),
                        tofile=f"{source} (codemod)",
                    )
                ),
                end="",
            )
    return 1 if result.diagnostics else 0
