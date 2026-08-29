"""CLI entries for the non-executing Hedron migration assistants."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from hedron.migrate.api import ApiMigrationReport

from hedron.migrate.analyze import analyze_source
from hedron.migrate.findings import finding_for_code, plan_to_diagnostics
from hedron.migrate.generate import generate_project
from hedron.migrate.report import format_report
from hedron_core.diagnostics import DiagnosticSeverity, meets_severity_threshold


class Subparsers(Protocol):
    """Minimal parser-factory contract required by migration subcommands."""

    def add_parser(self, name: str, *, help: str | None = None) -> argparse.ArgumentParser:
        """Create and return a named argument parser."""
        ...


def build_streamlit_parser(
    subparsers: Subparsers,
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
        choices=("3.10", "3.11", "3.12", "3.13", "3.14"),
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


def build_react_parser(
    subparsers: Subparsers,
) -> argparse.ArgumentParser:
    """Register the non-executing React disposition analyzer."""
    parser = subparsers.add_parser(
        "react",
        help="Statically report React migration dispositions (phase 0.63)",
    )
    parser.add_argument("source", help="React/TypeScript source file or directory")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.set_defaults(func=run_migrate_react_args)
    return parser


def build_api_parser(
    subparsers: Subparsers,
) -> argparse.ArgumentParser:
    """Register the 0.67-to-1.0 API migration scanner/transform."""
    parser = subparsers.add_parser(
        "api",
        help="Statically migrate transitional Hedron API paths to the 1.0 surface",
    )
    parser.add_argument(
        "source",
        nargs="?",
        default=".",
        help="Python file or project directory (default: current directory)",
    )
    parser.add_argument("--target", choices=("1.0",), required=True)
    parser.add_argument(
        "--out",
        default=None,
        help="Write transformed files to a new directory/file (never overwrites)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply proven replacements in place; manual findings remain untouched",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Print a unified diff for proven replacements",
    )
    parser.add_argument("--format", choices=("text", "json", "sarif"), default="text")
    parser.set_defaults(func=run_migrate_api_args)
    return parser


def run_migrate_api_args(args: argparse.Namespace) -> int:
    try:
        report = run_migrate_api(
            source=Path(args.source),
            out=Path(args.out) if args.out else None,
            apply=bool(args.apply),
            fmt=str(args.format),
            show_diff=bool(args.diff),
        )
    except (FileNotFoundError, FileExistsError, OSError, ValueError) as exc:
        print(f"API migration failed: {exc}", file=sys.stderr)
        return 1
    return 2 if report.requires_review else 0


def run_migrate_api(
    *,
    source: Path,
    out: Path | None = None,
    apply: bool = False,
    fmt: str = "text",
    show_diff: bool = False,
) -> ApiMigrationReport:
    """Scan and optionally transform API paths without importing target code."""
    from hedron.migrate.api import transform_api, unified_diff
    from hedron_core.diagnostics import diagnostics_to_sarif

    diff = unified_diff(source) if show_diff else ""
    report = transform_api(source, output=out, apply=apply)
    if fmt == "json":
        print(report.to_json(), end="")
    elif fmt == "sarif":
        import json as _json

        print(_json.dumps(diagnostics_to_sarif(report.diagnostics()), indent=2, sort_keys=True))
    else:
        print(f"API migration source: {report.source}")
        print(f"Non-executing: {report.non_executing}")
        print(f"Files: {report.files_seen}  Findings: {len(report.findings)}")
        for finding in report.findings:
            print(
                f"- {finding.code} {finding.old_path} -> {finding.replacement} "
                f"({finding.path}:{finding.line}:{finding.column}; "
                f"confidence={finding.confidence}, automation={finding.automation_status})"
            )
        if report.changes:
            print("Changed files:")
            for change in report.changes:
                print(f"- {change.path}: {change.replacements} replacement(s)")
        if show_diff and diff:
            print(diff, end="")
        if report.requires_review:
            print("REVIEW REQUIRED", file=sys.stderr)
    return report


def run_migrate_react_args(args: argparse.Namespace) -> int:
    return run_migrate_react(source=Path(args.source), fmt=str(args.format))


def run_migrate_react(*, source: Path, fmt: str = "text") -> int:
    from hedron.migrate.react import analyze_react_source

    try:
        payload = analyze_react_source(source)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"React migration analysis failed: {exc}", file=sys.stderr)
        return 1
    if fmt == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"React source: {payload['source']}")
        print(f"Non-executing: {payload['non_executing']}")
        print(f"Files: {payload['files_seen']}  Bytes: {payload['bytes_seen']}")
        for disposition, count in payload["disposition_counts"].items():
            print(f"{disposition}: {count}")
        for finding in payload["findings"]:
            span = finding.get("span", {})
            print(
                f"- {finding['disposition']} {finding['kind']} "
                f"({span.get('path')}:{span.get('start_line')}:{span.get('start_column')})"
            )
    return 0


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
