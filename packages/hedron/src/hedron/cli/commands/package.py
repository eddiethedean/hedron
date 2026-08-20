"""CLI command: external package-author doctor (DOCTOR-054)."""

from __future__ import annotations

import argparse
import json


def _cmd_package_doctor(args: argparse.Namespace) -> int:
    from hedron.package_doctor import diagnose_package

    report = diagnose_package(args.path)
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True, default=str))
    else:
        package = report.get("package") or {}
        print(
            f"package_doctor={report.get('package_doctor')} ok={report.get('ok')} "
            f"read_only={report.get('read_only')}"
        )
        print(f"{package.get('name')} {package.get('version')} ({report.get('root')})")
        for name, check in sorted((report.get("checks") or {}).items()):
            print(f"- {name}: {'ok' if check.get('ok') else 'failed'}")
        for diagnostic in report.get("diagnostics") or []:
            print(
                f"{diagnostic.get('code')} [{diagnostic.get('severity')}] "
                f"{diagnostic.get('message')}"
            )
    return 0 if report.get("ok") else 1
