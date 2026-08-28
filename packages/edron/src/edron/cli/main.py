from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from edron.deployment import PROFILE_NAMES, check_deployment
from edron.diagnostics import DiagnosticReport, finding
from edron.migrate.cli import build_migrate_parser
from edron.scaffolds import TEMPLATES, create_scaffold
from edron.tooling import check_source, doctor, explain_application, load_application


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
    command.add_argument(
        "--profile",
        metavar="PROFILE",
        default=None,
        help=f"deployment profile ({', '.join(PROFILE_NAMES)})",
    )
    command.add_argument("--bind", default=None)
    command.add_argument("--port", type=int, default=None)
    command.add_argument("--workers", type=int, default=None)
    command.add_argument("--root-path", default=None)
    command.add_argument("--build-dir", type=Path, default=None)
    command.add_argument("--external-url", default=None)
    command.add_argument("--trust-proxy", action="append", default=None)
    command.add_argument(
        "--state-backend", choices=("process-local", "shared", "unknown"), default=None
    )
    command.add_argument(
        "--job-backend", choices=("process-local", "shared", "unknown"), default=None
    )
    command.add_argument("--secret-source", default=None, help="opaque platform secret reference")


def _deployment_overrides(args: argparse.Namespace) -> dict[str, object]:
    values = {
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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="edron")
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="run a trusted Edron application")
    run.add_argument("application", help="app.py or module:attribute")
    run.add_argument("--host", default="127.0.0.1")
    run.add_argument("--port", type=int, default=8000)
    run.add_argument("--reload", action="store_true")

    deploy_check = sub.add_parser(
        "deploy-check", help="validate an explicit deployment profile without importing the app"
    )
    _add_deployment_arguments(deploy_check)
    deploy_check.add_argument("--format", choices=("text", "json", "sarif"), default="text")
    deploy_check.add_argument("--cwd", type=Path, default=None)

    check = sub.add_parser("check", help="statically check an Edron source file")
    check.add_argument("application", help="app.py or module:attribute")
    check.add_argument("--register", action="store_true", help="also import trusted source")
    check.add_argument("--format", choices=("text", "json", "sarif"), default="text")
    check.add_argument("--fail-on", choices=("information", "warning", "error"), default="error")

    explain = sub.add_parser("explain", help="explain registered Edron surfaces")
    explain.add_argument("application", help="app.py or module:attribute")
    explain.add_argument("--format", choices=("text", "json"), default="text")

    doctor_parser = sub.add_parser("doctor", help="diagnose package capabilities")
    doctor_parser.add_argument(
        "application", nargs="?", help="optional trusted app.py or module:attribute"
    )
    doctor_parser.add_argument("--format", choices=("text", "json"), default="text")
    _add_deployment_arguments(doctor_parser)
    doctor_parser.add_argument("--cwd", type=Path, default=None)

    new = sub.add_parser("new", help="create an Edron teaching scaffold")
    new.add_argument("name")
    new.add_argument("--path", type=Path, default=None)
    new.add_argument("--template", choices=TEMPLATES, default="minimal")
    new.add_argument("--overwrite", action="store_true")

    build_migrate_parser(sub)

    args = parser.parse_args(argv)
    try:
        if hasattr(args, "func"):
            return args.func(args)
        if args.command == "run":
            import uvicorn

            if args.reload:
                if ":" not in args.application or Path(args.application).is_file():
                    raise ValueError(
                        "--reload requires an import target such as app:app; "
                        "a loaded application object cannot be re-imported by Uvicorn"
                    )
                uvicorn.run(args.application, host=args.host, port=args.port, reload=True)
            else:
                application = load_application(args.application)
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
            if ":" in args.application and not Path(args.application).is_file():
                if not args.register:
                    report = _app_failure(
                        "static check requires a .py file unless --register is supplied"
                    )
                else:
                    load_application(args.application)
                    report = DiagnosticReport()
            else:
                report = check_source(args.application)
                if args.register and report.ok:
                    load_application(args.application)
            _print_report(report, args.format)
            return _report_status(report, args.fail_on)
        if args.command == "explain":
            application = load_application(args.application)
            payload = explain_application(application)
            if args.format == "json":
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"Edron application: {payload.get('title', '<unnamed>')}")
                for page in payload.get("pages", []):
                    print(f"- {page.get('name')} {page.get('path')}: {page.get('title')}")
                    for surface in page.get("surfaces", []):
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
                    for item in payload[group]:
                        version = f" {item['version']}" if item.get("version") else ""
                        print(f"  {item['name']}: {item['status']}{version}")
            deployment = payload.get("deployment")
            return 0 if not isinstance(deployment, dict) or deployment.get("ok", True) else 2
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
