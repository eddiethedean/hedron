"""CLI entry for ``hedron migrate streamlit``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from hedron.migrate.analyze import analyze_source
from hedron.migrate.findings import finding_for_code, plan_to_diagnostics
from hedron.migrate.generate import generate_project
from hedron.migrate.report import format_report
from hedron_core.diagnostics import DiagnosticSeverity, meets_severity_threshold


def build_streamlit_parser(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "streamlit",
        help="Statically migrate a Streamlit app to a Hedron scaffold (RFC-0061)",
    )
    parser.add_argument("source", help="Streamlit entrypoint (.py) or project directory")
    parser.add_argument(
        "--out",
        default=None,
        help="New output directory (required unless --analyze-only)",
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="Boundary for local-module discovery (default: nearest pyproject.toml)",
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Produce the migration report without generating a project",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json", "sarif"),
        default="text",
        help="Report format",
    )
    parser.add_argument(
        "--python-version",
        choices=("3.11", "3.12", "3.13", "3.14"),
        default="3.12",
        help="Parser grammar for the input source",
    )
    parser.add_argument(
        "--fail-on",
        choices=("information", "warning", "error"),
        default="error",
        help="Exit 2 when findings meet or exceed this severity (default: error)",
    )
    parser.set_defaults(func=run_migrate_streamlit_args)
    return parser


def run_migrate_streamlit_args(args: argparse.Namespace) -> int:
    return run_migrate_streamlit(
        source=Path(args.source),
        out=Path(args.out) if args.out else None,
        project_root=Path(args.project_root) if args.project_root else None,
        analyze_only=bool(args.analyze_only),
        fmt=str(args.format),
        python_version=str(args.python_version),
        fail_on=str(args.fail_on),
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
    """Run analysis (and optional generation). Exit codes: 0 / 1 / 2 per RFC-0061."""
    if not analyze_only and out is None:
        print("--out is required unless --analyze-only is set", file=sys.stderr)
        return 1

    plan = analyze_source(
        source,
        project_root=project_root,
        python_version=python_version,
    )
    diagnostics = plan_to_diagnostics(plan)
    generated: dict[str, str] = {}

    if plan.tool_errors:
        sys.stdout.write(format_report(plan, diagnostics, fmt=fmt))
        return 1

    if not analyze_only:
        if out is None:
            raise RuntimeError("migration generate requires --out when not analyze-only")
        try:
            generated = generate_project(plan, out)
        except FileExistsError as exc:
            diagnostics = [
                finding_for_code(
                    "HED-MIG-ST-0012",
                    explanation=str(exc),
                    remediation="Choose a fresh empty --out directory.",
                ),
                *diagnostics,
            ]
            sys.stdout.write(format_report(plan, diagnostics, fmt=fmt))
            return 1
        except (OSError, RuntimeError, ValueError) as exc:
            diagnostics = [
                finding_for_code(
                    "HED-MIG-ST-0012",
                    explanation=str(exc),
                    remediation="Fix generation errors and retry with an empty --out.",
                ),
                *diagnostics,
            ]
            sys.stdout.write(format_report(plan, diagnostics, fmt=fmt))
            return 1

    sys.stdout.write(format_report(plan, diagnostics, fmt=fmt, generated_files=generated or None))

    threshold = DiagnosticSeverity(fail_on)
    if meets_severity_threshold(diagnostics, threshold):
        print("REVIEW REQUIRED", file=sys.stderr)
        return 2
    return 0
