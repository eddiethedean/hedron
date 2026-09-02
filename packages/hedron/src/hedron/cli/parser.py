"""Argument parser and ``main`` entry for the Hedron CLI."""

from __future__ import annotations

import argparse
from typing import Protocol

from hedron.cli.commands.accel_status import cmd_accel_status
from hedron.cli.commands.audit_components import cmd_audit_components
from hedron.cli.commands.build import cmd_build
from hedron.cli.commands.check import cmd_check
from hedron.cli.commands.conformance import cmd_conformance
from hedron.cli.commands.dev import cmd_dev
from hedron.cli.commands.discover import cmd_discover
from hedron.cli.commands.eject import cmd_eject
from hedron.cli.commands.explain import cmd_explain
from hedron.cli.commands.fleet import cmd_fleet
from hedron.cli.commands.graph import cmd_graph
from hedron.cli.commands.inspect import cmd_inspect
from hedron.cli.commands.new import cmd_new
from hedron.cli.commands.package import cmd_package_doctor
from hedron.cli.commands.routes import cmd_components, cmd_preview, cmd_routes
from hedron.cli.commands.run import cmd_run_app
from hedron.cli.commands.security_check import cmd_security_check
from hedron.cli.commands.style import (
    cmd_style_conform,
    cmd_style_custom_css_check,
    cmd_style_diff,
    cmd_style_eject,
    cmd_style_eject_application,
    cmd_style_explain,
    cmd_style_init,
    cmd_style_inspect,
    cmd_style_package,
    cmd_style_preview,
    cmd_style_update_check,
)
from hedron.cli.commands.testgen import cmd_testgen
from hedron.cli.commands.theme import (
    cmd_style_check,
    cmd_theme_check,
    cmd_theme_contract,
    cmd_theme_export,
    cmd_theme_inspect,
    cmd_theme_manifest,
    cmd_theme_matrix,
    cmd_theme_metadata,
)
from hedron.cli.commands.upgrade_report import cmd_upgrade_report


class _Subparsers(Protocol):
    def add_parser(self, name: str, *, help: str | None = None) -> argparse.ArgumentParser: ...


def _cmd_style_check_dispatch(args: argparse.Namespace) -> int:
    if args.custom_css:
        return cmd_style_custom_css_check(args)
    return cmd_style_check(args)


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    raise SystemExit(args.func(args))


def _build_parser() -> argparse.ArgumentParser:
    """Assemble the root ``hedron`` CLI parser and all subcommands."""
    parser = argparse.ArgumentParser(prog="hedron", description="Hedron CLI")
    parser.add_argument(
        "--app",
        help="Import path to an application factory or instance (module:attr)",
        default=None,
    )
    sub = parser.add_subparsers(dest="command", required=True)
    _register_catalog_commands(sub)
    _register_inspect_commands(sub)
    _register_scaffold_commands(sub)
    _register_check_commands(sub)
    _register_discovery_commands(sub)
    _register_package_commands(sub)
    _register_audit_commands(sub)
    _register_runtime_commands(sub)
    _register_theme_commands(sub)
    _register_migrate_commands(sub)
    _register_upgrade_commands(sub)
    return parser


def _register_catalog_commands(sub: _Subparsers) -> None:
    """Register routes/components/preview/testgen subcommands."""
    routes_p = sub.add_parser("routes", help="List registered Hedron routes")
    routes_p.add_argument(
        "--document",
        action="store_true",
        help="Emit a versioned typed route document (hedron-route-document-1)",
    )
    routes_p.set_defaults(func=cmd_routes)

    components_p = sub.add_parser("components", help="List registered components")
    components_p.set_defaults(func=cmd_components)

    preview_p = sub.add_parser("preview", help="Inspect a route/component preview")
    preview_p.add_argument("logical_id", help="Route logical id or name")
    preview_p.set_defaults(func=cmd_preview)

    testgen_p = sub.add_parser(
        "testgen",
        help="Generate reviewable interaction pytest stubs from a sealed catalog",
    )
    testgen_p.add_argument(
        "--profile",
        default="default",
        help="Generator profile label embedded in the source (default: default)",
    )
    testgen_p.add_argument(
        "--generator-version",
        default=None,
        help="Override embedded generator version (default: package GENERATOR_VERSION)",
    )
    testgen_p.add_argument(
        "--out",
        default=None,
        help="Write source to a file instead of stdout",
    )
    testgen_p.set_defaults(func=cmd_testgen)


def _register_inspect_commands(sub: _Subparsers) -> None:
    """Register inspect and eject subcommands."""
    inspect_p = sub.add_parser(
        "inspect",
        help="Explain a component's styles, dependencies, and accessibility contract",
    )
    inspect_p.add_argument(
        "component",
        help="Component name, logical id, 'interactions', 'features', or 'htmx-extensions'",
    )
    inspect_p.add_argument("--json", action="store_true", help="Emit versioned JSON")
    inspect_p.add_argument(
        "--static",
        nargs="?",
        const=".",
        default=None,
        help="Static/no-import inspect of a project root (interactions only)",
    )
    inspect_p.add_argument(
        "--manifest",
        default=None,
        help="Read an existing interactions.json without importing the app",
    )
    inspect_p.set_defaults(func=cmd_inspect)

    eject_p = sub.add_parser(
        "eject",
        help="Eject accessibility_contract.json and editable local CSS overrides",
    )
    eject_p.add_argument("component", help="Component name, logical id, or 'features:<bundle-id>'")
    eject_p.add_argument(
        "--out",
        "--output",
        dest="out",
        help="Output directory (project-relative)",
    )
    eject_p.add_argument(
        "--force",
        "--overwrite",
        dest="force",
        action="store_true",
        help="Overwrite existing ejected files",
    )
    eject_p.add_argument(
        "--surface",
        default=None,
        help="Feature surface name to select when ejecting features:ID",
    )
    eject_p.set_defaults(func=cmd_eject)

    explain_p = sub.add_parser(
        "explain",
        help="Explain an included feature (static redacted plan)",
    )
    explain_p.add_argument(
        "target",
        help="Explanation target (features:<logical-id>)",
    )
    explain_p.add_argument(
        "--format",
        choices=("human", "json"),
        default="human",
        help="Output format (default: human)",
    )
    explain_p.set_defaults(func=cmd_explain)


def _register_scaffold_commands(sub: _Subparsers) -> None:
    """Register build and new subcommands."""
    build_p = sub.add_parser("build", help="Compile CSS/assets into a build manifest")
    build_p.add_argument("--project", default=None)
    build_p.add_argument("--dev", action="store_true", help="Use readable development names")
    build_p.set_defaults(func=cmd_build)

    new_p = sub.add_parser("new", help="Scaffold a Hedron application or element")
    new_p.add_argument("name", help="Project name, or 'element'")
    new_p.add_argument("element_name", nargs="?", default=None, help="Element package name")
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
    new_p.add_argument(
        "--template",
        choices=("minimal", "crud", "dashboard", "task"),
        default="minimal",
        help="FastAPI scaffold template (default: minimal)",
    )
    new_p.set_defaults(func=cmd_new)


def _register_check_commands(sub: _Subparsers) -> None:
    """Register check and security-check subcommands."""
    check_p = sub.add_parser("check", help="Run project diagnostics")
    check_p.add_argument("--project", default=None)
    check_p.add_argument(
        "--target",
        choices=("1.0",),
        default=None,
        help="Report structured migration findings for the Hedron 1.0 surface",
    )
    check_p.add_argument(
        "--phase-063",
        dest="phase063",
        action="store_true",
        help="Run bounded non-executing phase 0.63 interaction/theme checks",
    )
    check_p.add_argument(
        "--format",
        choices=("text", "json", "sarif"),
        default="text",
    )
    check_p.add_argument(
        "--severity",
        default="error",
        help=(
            "Fail when diagnostics meet or exceed this severity "
            "(error|err, warning|warn, information|info|note)"
        ),
    )
    check_p.add_argument(
        "--version",
        default=None,
        help=(
            "Living-train version for applicability filtering "
            "(default: installed hedron package version)"
        ),
    )
    check_p.add_argument(
        "--all-compat",
        action="store_true",
        help=(
            "Include global adapter/extra compatibility notices even when those "
            "integrations are not detected in the project under check"
        ),
    )
    check_p.set_defaults(func=cmd_check)

    security_check_p = sub.add_parser(
        "security-check",
        help="Offline security posture report (read-only; does not probe production)",
    )
    security_check_p.add_argument("--project", default=None)
    security_check_p.add_argument(
        "--format",
        choices=("text", "json", "sarif"),
        default="text",
    )
    security_check_p.add_argument(
        "--policy",
        default="standard",
        help="SecurityPolicy preset name (development|standard|strict)",
    )
    security_check_p.add_argument("--suppressions", default=None, help="JSON suppressions file")
    security_check_p.add_argument(
        "--baseline",
        default=None,
        help="Reviewed baseline fingerprints JSON",
    )
    security_check_p.add_argument(
        "--strict",
        action="store_true",
        help="Fail on proven warnings and baseline drift",
    )
    security_check_p.set_defaults(func=cmd_security_check)


def _register_discovery_commands(sub: _Subparsers) -> None:
    """Register discover and fleet subcommands."""
    discover_p = sub.add_parser(
        "discover",
        help="List curated public API names with stability inventory tags",
    )
    discover_p.add_argument(
        "--format",
        choices=("human", "json"),
        default="json",
        help="Output format (default: json)",
    )
    discover_p.set_defaults(func=cmd_discover)

    fleet_p = sub.add_parser(
        "fleet",
        help="Read-only diagnosis of installed hedron train/extras/plugins/assets",
    )
    fleet_p.add_argument(
        "--format",
        choices=("json", "human"),
        default="json",
        help="Output format (default: json)",
    )
    fleet_p.set_defaults(func=cmd_fleet)


def _register_package_commands(sub: _Subparsers) -> None:
    """Register package doctor subcommands."""
    package_p = sub.add_parser(
        "package",
        help="External package-author tooling for Hedron plugin distributions",
    )
    package_sub = package_p.add_subparsers(dest="package_command", required=True)
    package_doctor_p = package_sub.add_parser(
        "doctor",
        help="Read-only validation of a package source tree (distinct from 'hedron fleet')",
    )
    package_doctor_p.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Package root containing pyproject.toml (default: .)",
    )
    package_doctor_p.add_argument(
        "--format",
        choices=("json", "human"),
        default="json",
        help="Output format (default: json)",
    )
    package_doctor_p.set_defaults(func=cmd_package_doctor)


def _register_audit_commands(sub: _Subparsers) -> None:
    """Register graph, audit-components, conformance, and accel-status."""
    graph_p = sub.add_parser("graph", help="Component dependency graph")
    graph_p.set_defaults(func=cmd_graph)

    audit_p = sub.add_parser("audit-components", help="Capability and package audit")
    audit_p.set_defaults(func=cmd_audit_components)

    conf_p = sub.add_parser(
        "conformance",
        help="Run the published language-neutral conformance kit (requires hedron[conformance])",
    )
    conf_p.add_argument("--json", action="store_true", help="Emit JSON report")
    conf_p.set_defaults(func=cmd_conformance)

    accel_p = sub.add_parser(
        "accel-status",
        help="Report optional hedron-native acceleration status",
    )
    accel_p.set_defaults(func=cmd_accel_status)


def _register_runtime_commands(sub: _Subparsers) -> None:
    """Register dev and run subcommands."""
    dev_p = sub.add_parser("dev", help="Watch Python/Jinja/CSS/assets and rebuild atomically")
    dev_p.add_argument("--project", default=None)
    dev_p.add_argument("--interval", type=float, default=0.5)
    dev_p.add_argument("--once", action="store_true", help="Build once and exit")
    dev_p.set_defaults(func=cmd_dev)

    run_p = sub.add_parser(
        "run",
        help="Run an ASGI app; auto-use hedron-posit inside Posit Workbench",
    )
    run_p.add_argument("target", nargs="?", help="module:app or module:factory")
    run_p.add_argument("--factory", action="store_true")
    run_p.add_argument("--host")
    run_p.add_argument("--port", type=int)
    run_p.add_argument("--reload", action="store_true")
    run_p.add_argument("--workers", type=int, default=1)
    run_p.add_argument("--debug", action="store_true")
    run_p.add_argument("--workbench", action="store_true")
    run_p.add_argument(
        "--discover",
        action="store_true",
        help="Bind then discover the Workbench mount even without RS_SERVER_URL",
    )
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
    run_p.set_defaults(func=cmd_run_app)


def _register_theme_commands(sub: _Subparsers) -> None:
    """Register theme and style subcommands."""
    theme_p = sub.add_parser("theme", help="Theme token and contrast diagnostics")
    theme_sub = theme_p.add_subparsers(dest="theme_command", required=True)
    theme_check_p = theme_sub.add_parser(
        "check",
        help="Validate theme tokens, element compatibility, and contrast basics",
    )
    theme_check_p.add_argument(
        "--theme",
        action="append",
        default=None,
        help="Theme name to check (repeatable; default: every built-in theme)",
    )
    theme_check_p.add_argument("--format", choices=("text", "json"), default="text")
    theme_check_p.add_argument(
        "--severity",
        default="error",
        help="Fail when diagnostics meet or exceed this severity (error|warning|info)",
    )
    theme_check_p.set_defaults(func=cmd_theme_check)

    theme_export_p = theme_sub.add_parser(
        "export",
        help="Export a resolved theme as CSS, design-token JSON, or a full report",
    )
    theme_export_p.add_argument("--theme", dest="theme_name", default="default")
    theme_export_p.add_argument("--spec", default=None, help="ThemeSpec JSON input")
    theme_export_p.add_argument(
        "--profile",
        choices=("core", "forms", "data", "workflow", "complete"),
        default="core",
    )
    theme_export_p.add_argument("--format", choices=("css", "json", "report"), default="json")
    theme_export_p.add_argument("--output", default=None)
    theme_export_p.set_defaults(func=cmd_theme_export)

    theme_manifest_p = theme_sub.add_parser(
        "manifest", help="Emit the registry-derived component theme manifest"
    )
    theme_manifest_p.add_argument("--output", default=None)
    theme_manifest_p.set_defaults(func=cmd_theme_manifest)

    theme_metadata_p = theme_sub.add_parser(
        "metadata", help="Emit registry-derived custom-element metadata"
    )
    theme_metadata_p.add_argument("--output", default=None)
    theme_metadata_p.set_defaults(func=cmd_theme_metadata)

    theme_matrix_p = theme_sub.add_parser("matrix", help="Emit the bounded component state matrix")
    theme_matrix_p.add_argument("--component", action="append", default=None)
    theme_matrix_p.add_argument("--viewport", action="append", default=None)
    theme_matrix_p.add_argument("--mode", action="append", default=None)
    theme_matrix_p.add_argument("--accessibility-mode", action="append", default=None)
    theme_matrix_p.add_argument("--output", default=None)
    theme_matrix_p.set_defaults(func=cmd_theme_matrix)

    theme_contract_p = theme_sub.add_parser(
        "contract", help="Emit the complete theme-contract evidence report"
    )
    theme_contract_p.add_argument("--theme", dest="theme_name", default="default")
    theme_contract_p.add_argument("--spec", default=None, help="ThemeSpec JSON input")
    theme_contract_p.add_argument("--stylesheet", default=None)
    theme_contract_p.add_argument("--output", default=None)
    theme_contract_p.set_defaults(func=cmd_theme_contract)

    theme_inspect_p = theme_sub.add_parser(
        "inspect", help="Inspect stylesheet compatibility consumers"
    )
    theme_inspect_p.add_argument("--stylesheet", required=True)
    theme_inspect_p.add_argument("--output", default=None)
    theme_inspect_p.set_defaults(func=cmd_theme_inspect)

    style_p = sub.add_parser("style", help="Application presentation audits and design tooling")
    style_sub = style_p.add_subparsers(dest="style_command", required=True)
    style_check_p = style_sub.add_parser(
        "check",
        help="Audit a path for application-authored CSS",
    )
    style_check_group = style_check_p.add_mutually_exclusive_group(required=True)
    style_check_group.add_argument(
        "--zero-app-css",
        dest="zero_app_css",
        help="Fail when stylesheets or inline style blocks exist under this path",
    )
    style_check_group.add_argument(
        "--custom-css",
        dest="custom_css",
        help="Validate explicitly registered-style CSS under this path",
    )
    style_check_p.add_argument("--format", choices=("text", "json"), default="text")
    style_check_p.set_defaults(func=_cmd_style_check_dispatch)

    style_inspect_p = style_sub.add_parser(
        "inspect",
        help="Inspect registered application styles, cascade order, and public hooks",
    )
    style_inspect_p.add_argument("--format", choices=("human", "json"), default="human")
    style_inspect_p.set_defaults(func=cmd_style_inspect)

    style_explain_p = style_sub.add_parser(
        "explain",
        help="Explain a DesignSystem / theme plan",
    )
    style_explain_p.add_argument("surface", nargs="?", help="Public component.part surface")
    style_explain_p.add_argument("--property", default=None)
    style_explain_p.add_argument(
        "--design",
        default=None,
        help="Design or theme name (default: app theme or 'default')",
    )
    style_explain_p.add_argument(
        "--format",
        choices=("human", "json"),
        default="human",
    )
    style_explain_p.set_defaults(func=cmd_style_explain)

    style_preview_p = style_sub.add_parser(
        "preview",
        help="Write a fixed data-free design gallery HTML file",
    )
    style_preview_p.add_argument(
        "--design",
        default=None,
        help="Design or theme name (default: app theme or 'default')",
    )
    style_preview_p.add_argument(
        "--output",
        required=True,
        help="Output HTML file or directory (project-relative)",
    )
    style_preview_p.add_argument(
        "--mode",
        choices=("all", "light", "dark"),
        default="all",
    )
    style_preview_p.set_defaults(func=cmd_style_preview)

    style_diff_p = style_sub.add_parser(
        "diff",
        help="Diff two designs/themes or an ejected application stylesheet",
    )
    style_diff_p.add_argument("base", nargs="?", help="Base design/theme name")
    style_diff_p.add_argument("candidate", nargs="?", help="Candidate design/theme name")
    style_diff_p.add_argument(
        "--ejected-path",
        default=None,
        help="Ejected application stylesheet directory or source map",
    )
    style_diff_p.add_argument(
        "--manifest",
        default=None,
        help="Application ejection source map (defaults beside --ejected-path)",
    )
    style_diff_p.add_argument(
        "--format",
        choices=("human", "json"),
        default="human",
    )
    style_diff_p.set_defaults(func=cmd_style_diff)

    style_update_p = style_sub.add_parser(
        "update",
        help="Check ejected application CSS for source drift",
    )
    style_update_p.add_argument("--check", action="store_true", required=True)
    style_update_p.add_argument("--manifest", default=None)
    style_update_p.add_argument("--format", choices=("human", "json"), default="human")
    style_update_p.set_defaults(func=cmd_style_update_check)

    style_eject_p = style_sub.add_parser(
        "eject",
        help="Eject a design/theme (whole or partial) to reviewable Theme Python",
    )
    style_eject_p.add_argument("name", help="Design or theme name to eject")
    style_eject_p.add_argument("--group", default=None, help="Eject one typed design group")
    style_eject_p.add_argument("--recipe", default=None, help="Eject one named recipe")
    style_eject_p.add_argument(
        "--component",
        default=None,
        help="Eject selection annotated for one component id",
    )
    style_eject_p.add_argument(
        "--output",
        required=True,
        help="Output directory (project-relative)",
    )
    style_eject_p.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing ejected files",
    )
    style_eject_p.set_defaults(func=cmd_style_eject)

    style_eject_app_p = style_sub.add_parser(
        "eject-css",
        help="Eject registered application CSS with a provenance source map",
    )
    style_eject_app_p.add_argument("--output", required=True)
    style_eject_app_p.add_argument("--overwrite", action="store_true")
    style_eject_app_p.set_defaults(func=cmd_style_eject_application)

    style_init_p = style_sub.add_parser(
        "init",
        help="Write a non-overwriting starter ThemeSpec JSON",
    )
    style_init_p.add_argument("--name", default="custom")
    style_init_p.add_argument("--output", required=True)
    style_init_p.set_defaults(func=cmd_style_init)

    style_package_p = style_sub.add_parser(
        "package",
        help="Validate and package a ThemeSpec as data-only JSON/ZIP",
    )
    style_package_p.add_argument("--spec", required=True)
    style_package_p.add_argument("--output", required=True)
    style_package_p.add_argument(
        "--profile",
        choices=("core", "forms", "data", "workflow", "complete"),
        default="core",
    )
    style_package_p.add_argument("--license", action="append", default=None)
    style_package_p.add_argument("--overwrite", action="store_true")
    style_package_p.set_defaults(func=cmd_style_package)

    style_conform_p = style_sub.add_parser(
        "conform",
        help="Emit the portable declared-profile ThemeSpec conformance report",
    )
    style_conform_p.add_argument("--spec", required=True)
    style_conform_p.add_argument(
        "--profile",
        choices=("core", "forms", "data", "workflow", "complete"),
        default=None,
    )
    style_conform_p.set_defaults(func=cmd_style_conform)


def _register_migrate_commands(sub: _Subparsers) -> None:
    """Register migrate assistants."""
    migrate_p = sub.add_parser(
        "migrate",
        help="Reviewable framework migration assistants (RFC-0061)",
    )
    migrate_sub = migrate_p.add_subparsers(dest="migrate_command", required=True)
    from hedron.migrate.cli import build_api_parser, build_react_parser, build_streamlit_parser

    build_api_parser(migrate_sub)
    build_streamlit_parser(migrate_sub)
    build_react_parser(migrate_sub)


def _register_upgrade_commands(sub: _Subparsers) -> None:
    """Register upgrade-report."""
    upgrade_p = sub.add_parser(
        "upgrade-report",
        help="Offline application upgrade compatibility report (0.55)",
    )
    upgrade_p.add_argument("--from", dest="from_version", required=True, help="Current train tip")
    upgrade_p.add_argument("--to", dest="to_version", required=True, help="Target train tip")
    upgrade_p.add_argument(
        "--baseline",
        default=None,
        help="Reviewed baseline JSON path (fail closed on schema mismatch)",
    )
    upgrade_p.add_argument(
        "--manifest",
        default=None,
        help="Application WorkflowManifest JSON for definite/heuristic findings",
    )
    upgrade_p.add_argument("--out", default=None, help="Write JSON report to a file")
    upgrade_p.add_argument(
        "--allow-definite",
        action="store_true",
        help="Exit 0 even when definite breaks are present",
    )
    upgrade_p.set_defaults(func=cmd_upgrade_report)


if __name__ == "__main__":
    main()
