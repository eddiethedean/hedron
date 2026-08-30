"""CLI command: external package-author doctor (DOCTOR-054)."""

from __future__ import annotations

import argparse
import json
from typing import Any, cast


def _mapping(value: object) -> dict[str, Any]:
    return cast(dict[str, Any], value) if isinstance(value, dict) else {}


def _cmd_package_doctor(args: argparse.Namespace) -> int:
    from hedron.package_doctor import diagnose_package

    report = diagnose_package(args.path)
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True, default=str))
    else:
        package = _mapping(report.get("package"))
        print(
            f"package_doctor={report.get('package_doctor')} ok={report.get('ok')} "
            f"read_only={report.get('read_only')}"
        )
        print(f"{package.get('name')} {package.get('version')} ({report.get('root')})")
        for name, check_value in sorted(_mapping(report.get("checks")).items()):
            check = _mapping(check_value)
            print(f"- {name}: {'ok' if check.get('ok') else 'failed'}")
        diagnostics: object = report.get("diagnostics") or []
        for diagnostic_value in (
            cast(list[object], diagnostics) if isinstance(diagnostics, list) else []
        ):
            diagnostic = _mapping(diagnostic_value)
            print(
                f"{diagnostic.get('code')} [{diagnostic.get('severity')}] "
                f"{diagnostic.get('message')}"
            )
    return 0 if report.get("ok") else 1


cmd_package_doctor = _cmd_package_doctor
