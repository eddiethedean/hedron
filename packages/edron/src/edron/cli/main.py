from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Protocol, cast

from edron.deployment import PROFILE_NAMES, check_deployment
from edron.diagnostics import DiagnosticReport, finding
from edron.migrate.cli import build_migrate_parser
from edron.scaffolds import TEMPLATES, create_scaffold
from edron.tooling import check_source, doctor, explain_application, load_application
from hedron_core.typing_support import dynamic_attribute


class _ParsedArgs(Protocol):
    application: str | None
    bind: str | None
    build_dir: Path | None
    command: str | None
    cwd: Path | None
    external_url: str | None
    fail_on: str
    format: str
    func: Callable[[_ParsedArgs], int] | None
    host: str
    job_backend: str | None
    name: str
    overwrite: bool
    path: Path | None
    port: int
    profile: str | None
    register: bool
    reload: bool
    root_path: str | None
    secret_source: str | None
    state_backend: str | None
    template: str
    trust_proxy: list[str] | None
    workers: int | None


def _object_list(value: object) -> list[object] | None:
    return cast(list[object], value) if isinstance(value, list) else None


def _string_mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    mapping = cast(Mapping[object, object], value)
    if not all(isinstance(key, str) for key in mapping):
        return None
    return cast(Mapping[str, object], mapping)


def _print_report(report: DiagnosticReport, output_format: str) -> None:
    if output_format == "json":
        print(report.to_json(), end="")
    elif output_format == "sarif":
        print(json.dumps(report.to_sarif(), indent=2, sort_keys=True))
    else:
        print(report.to_text())


def _report_status(report: DiagnosticReport, fail_on: str) -> int:
    ranks = {"information": 0, "warning": 1, "error": 2}
    threshold = ranks[fail_on]
    return 0 if not any(ranks[item.severity] >= threshold for item in report.diagnostics) else 2


def _app_failure(message: str) -> DiagnosticReport:
    return DiagnosticReport(
        (
            finding(
                "EDR-TOOL-0007",
                severity="error",
                title="Application tooling failed",
                explanation=message,
                remediation="Fix the application or use --register only with trusted source.",
            ),
        )
    )


def _add_deployment_arguments(command: argparse.ArgumentParser) -> None:
    _ignored = command.add_argument(
        "--profile",
        metavar="PROFILE",
        default=None,
        help=f"deployment profile ({', '.join(PROFILE_NAMES)})",
    )
    _ignored = command.add_argument("--bind", default=None)
    _ignored = command.add_argument("--port", type=int, default=None)
    _ignored = command.add_argument("--workers", type=int, default=None)
    _ignored = command.add_argument("--root-path", default=None)
    _ignored = command.add_argument("--build-dir", type=Path, default=None)
    _ignored = command.add_argument("--external-url", default=None)
    _ignored = command.add_argument("--trust-proxy", action="append", default=None)
    _ignored = command.add_argument(
        "--state-backend", choices=("process-local", "shared", "unknown"), default=None
    )
    _ignored = command.add_argument(
        "--job-backend", choices=("process-local", "shared", "unknown"), default=None
    )
    _ignored = command.add_argument(
        "--secret-source", default=None, help="opaque platform secret reference"
    )


def _deployment_overrides(args: _ParsedArgs) -> dict[str, object]:
    values: dict[str, object] = {
        "bind": args.bind,
        "port": args.port,
        "workers": args.workers,
        "root_path": args.root_path,
        "build_dir": str(args.build_dir) if args.build_dir is not None else None,
        "external_url": args.external_url,
        "state_backend": args.state_backend,
        "job_backend": args.job_backend,
        "secret_source": args.secret_source,
    }
    if args.trust_proxy is not None:
        values["trust_proxy"] = tuple(args.trust_proxy)
    return {key: value for key, value in values.items() if value is not None}


def _required_application(args: _ParsedArgs) -> str:
    if not isinstance(args.application, str) or not args.application:
        raise SystemExit("this command requires an application target")
    return args.application


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="edron")
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="run a trusted Edron application")
    _ignored = run.add_argument("application", help="app.py or module:attribute")
    _ignored = run.add_argument("--host", default="127.0.0.1")
    _ignored = run.add_argument("--port", type=int, default=8000)
    _ignored = run.add_argument("--reload", action="store_true")

    deploy_check = sub.add_parser(
        "deploy-check", help="validate an explicit deployment profile without importing the app"
    )
    _add_deployment_arguments(deploy_check)
    _ignored = deploy_check.add_argument(
        "--format", choices=("text", "json", "sarif"), default="text"
    )
    _ignored = deploy_check.add_argument("--cwd", type=Path, default=None)

    check = sub.add_parser("check", help="statically check an Edron source file")
    _ignored = check.add_argument("application", help="app.py or module:attribute")
    _ignored = check.add_argument(
        "--register", action="store_true", help="also import trusted source"
    )
    _ignored = check.add_argument("--format", choices=("text", "json", "sarif"), default="text")
    _ignored = check.add_argument(
        "--fail-on", choices=("information", "warning", "error"), default="error"
    )

    explain = sub.add_parser("explain", help="explain registered Edron surfaces")
    _ignored = explain.add_argument("application", help="app.py or module:attribute")
    _ignored = explain.add_argument("--format", choices=("text", "json"), default="text")

    doctor_parser = sub.add_parser("doctor", help="diagnose package capabilities")
    _ignored = doctor_parser.add_argument(
        "application", nargs="?", help="optional trusted app.py or module:attribute"
    )
    _ignored = doctor_parser.add_argument("--format", choices=("text", "json"), default="text")
    _add_deployment_arguments(doctor_parser)
    _ignored = doctor_parser.add_argument("--cwd", type=Path, default=None)

    new = sub.add_parser("new", help="create an Edron teaching scaffold")
    _ignored = new.add_argument("name")
    _ignored = new.add_argument("--path", type=Path, default=None)
    _ignored = new.add_argument("--template", choices=TEMPLATES, default="minimal")
    _ignored = new.add_argument("--overwrite", action="store_true")

    build_migrate_parser(sub)

    args = cast(_ParsedArgs, cast(object, parser.parse_args(argv)))
    try:
        handler = dynamic_attribute(args, "func")
        if callable(handler):
            return cast(Callable[[object], int], handler)(args)
        if args.command == "run":
            import uvicorn
            from starlette.types import ASGIApp

            application_target = _required_application(args)

            if args.reload:
                if ":" not in application_target or Path(application_target).is_file():
                    raise ValueError(
                        "--reload requires an import target such as app:app; "
                        + "a loaded application object cannot be re-imported by Uvicorn"
                    )
                uvicorn.run(application_target, host=args.host, port=args.port, reload=True)
            else:
                application = cast(ASGIApp, load_application(application_target))
                uvicorn.run(application, host=args.host, port=args.port, reload=False)
            return 0
        if args.command == "deploy-check":
            report = check_deployment(
                args.profile,
                cwd=args.cwd,
                overrides=_deployment_overrides(args),
            )
            if args.format == "json":
                print(report.to_json(), end="")
            elif args.format == "sarif":
                print(json.dumps(report.to_sarif(), indent=2, sort_keys=True))
            else:
                print(report.to_text())
            return 0 if report.ok else 2
        if args.command == "check":
            application_target = _required_application(args)
            if ":" in application_target and not Path(application_target).is_file():
                if not args.register:
                    report = _app_failure(
                        "static check requires a .py file unless --register is supplied"
                    )
                else:
                    _ignored = load_application(application_target)
                    report = DiagnosticReport()
            else:
                report = check_source(application_target)
                if args.register and report.ok:
                    _ignored = load_application(application_target)
            _print_report(report, args.format)
            return _report_status(report, args.fail_on)
        if args.command == "explain":
            application = load_application(_required_application(args))
            payload = explain_application(application)
            if args.format == "json":
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"Edron application: {payload.get('title', '<unnamed>')}")
                pages = _object_list(payload.get("pages", [])) or []
                for page_value in pages:
                    page = _string_mapping(page_value)
                    if page is None:
                        continue
                    print(f"- {page.get('name')} {page.get('path')}: {page.get('title')}")
                    surfaces = _object_list(page.get("surfaces", [])) or []
                    for surface_value in surfaces:
                        surface = _string_mapping(surface_value)
                        if surface is None:
                            continue
                        print(
                            f"  - {surface.get('kind')} {surface.get('name')} {surface.get('path')}"
                        )
            return 0
        if args.command == "doctor":
            application = load_application(args.application) if args.application else None
            payload = doctor(
                application=application,
                deployment_profile=args.profile,
                deployment_overrides=_deployment_overrides(args),
                cwd=args.cwd,
            )
            if args.format == "json":
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                for group in ("required", "optional"):
                    print(f"{group}:")
                    items = _object_list(payload.get(group)) or []
                    for item_value in items:
                        item = _string_mapping(item_value)
                        if item is None:
                            continue
                        version = f" {item['version']}" if item.get("version") else ""
                        print(f"  {item['name']}: {item['status']}{version}")
            deployment = payload.get("deployment")
            if not isinstance(deployment, dict):
                return 0
            deployment = cast(dict[str, object], deployment)
            return 0 if deployment.get("ok", True) else 2
        if args.command == "new":
            destination = args.path or Path(args.name)
            files = create_scaffold(
                args.name, destination, template=args.template, overwrite=args.overwrite
            )
            print(
                json.dumps(
                    {
                        "created": str(destination),
                        "template": args.template,
                        "files": [str(item) for item in files],
                    },
                    indent=2,
                )
            )
            return 0
    except (OSError, RuntimeError, ValueError, AttributeError, ImportError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    parser.print_help()
    return 0
