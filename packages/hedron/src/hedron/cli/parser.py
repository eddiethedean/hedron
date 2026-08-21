"""Argument parser and ``main`` entry for the Hedron CLI."""

from __future__ import annotations

import argparse

from hedron.cli.commands.accel_status import _cmd_accel_status
from hedron.cli.commands.audit_components import _cmd_audit_components
from hedron.cli.commands.build import _cmd_build
from hedron.cli.commands.check import _cmd_check
from hedron.cli.commands.conformance import _cmd_conformance
from hedron.cli.commands.dev import _cmd_dev
from hedron.cli.commands.discover import _cmd_discover
from hedron.cli.commands.eject import _cmd_eject
from hedron.cli.commands.fleet import _cmd_fleet
from hedron.cli.commands.graph import _cmd_graph
from hedron.cli.commands.inspect import _cmd_inspect
from hedron.cli.commands.new import _cmd_new
from hedron.cli.commands.package import _cmd_package_doctor
from hedron.cli.commands.routes import _cmd_components, _cmd_preview, _cmd_routes
from hedron.cli.commands.run import _cmd_run_app
from hedron.cli.commands.testgen import _cmd_testgen
from hedron.cli.commands.theme import _cmd_style_check, _cmd_theme_check
from hedron.cli.commands.upgrade_report import _cmd_upgrade_report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="hedron", description="Hedron CLI")
    parser.add_argument(
        "--app",
        help="Import path to an application factory or instance (module:attr)",
        default=None,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    routes_p = sub.add_parser("routes", help="List registered Hedron routes")
    routes_p.add_argument(
        "--document",
        action="store_true",
        help="Emit a versioned typed route document (hedron-route-document-1)",
    )
    routes_p.set_defaults(func=_cmd_routes)

    components_p = sub.add_parser("components", help="List registered components")
    components_p.set_defaults(func=_cmd_components)

    preview_p = sub.add_parser("preview", help="Inspect a route/component preview")
    preview_p.add_argument("logical_id", help="Route logical id or name")
    preview_p.set_defaults(func=_cmd_preview)

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
    testgen_p.set_defaults(func=_cmd_testgen)

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
    inspect_p.set_defaults(func=_cmd_inspect)

    eject_p = sub.add_parser(
        "eject",
        help="Eject accessibility_contract.json and editable local CSS overrides",
    )
    eject_p.add_argument("component", help="Component name, logical id, or 'features:<bundle-id>'")
    eject_p.add_argument("--out", help="Output directory")
    eject_p.add_argument("--force", action="store_true")
    eject_p.set_defaults(func=_cmd_eject)

    build_p = sub.add_parser("build", help="Compile CSS/assets into a build manifest")
    build_p.add_argument("--project", default=None)
    build_p.add_argument("--dev", action="store_true", help="Use readable development names")
    build_p.set_defaults(func=_cmd_build)

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
    check_p.set_defaults(func=_cmd_check)

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
    discover_p.set_defaults(func=_cmd_discover)

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
    fleet_p.set_defaults(func=_cmd_fleet)

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
    package_doctor_p.set_defaults(func=_cmd_package_doctor)

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
    theme_check_p.set_defaults(func=_cmd_theme_check)

    style_p = sub.add_parser("style", help="Application presentation audits")
    style_sub = style_p.add_subparsers(dest="style_command", required=True)
    style_check_p = style_sub.add_parser(
        "check",
        help="Audit a path for application-authored CSS",
    )
    style_check_p.add_argument(
        "--zero-app-css",
        dest="zero_app_css",
        required=True,
        help="Fail when stylesheets or inline style blocks exist under this path",
    )
    style_check_p.add_argument("--format", choices=("text", "json"), default="text")
    style_check_p.set_defaults(func=_cmd_style_check)

    migrate_p = sub.add_parser(
        "migrate",
        help="Reviewable framework migration assistants (RFC-0061)",
    )
    migrate_sub = migrate_p.add_subparsers(dest="migrate_command", required=True)
    from hedron.migrate.cli import build_streamlit_parser

    build_streamlit_parser(migrate_sub)

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
    upgrade_p.add_argument("--out", default=None, help="Write JSON report to a file")
    upgrade_p.add_argument(
        "--allow-definite",
        action="store_true",
        help="Exit 0 even when definite breaks are present",
    )
    upgrade_p.set_defaults(func=_cmd_upgrade_report)

    args = parser.parse_args(argv)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
