#!/usr/bin/env python3
"""Verify phase 0.11 packaging evidence that can run without a public index."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    commands = [
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/adapters/flask/test_blueprint_factory.py",
            "tests/adapters/django/test_appconfig.py",
            "tests/adapters/django/test_forms_bridge.py",
            "tests/adapters/django/test_queryset_datasource.py",
            "tests/conformance/test_adapter_harness.py",
            "tests/jinja/test_hdj_0_11.py",
            "tests/conformance/test_job_backends_celery_rq.py",
            "tests/adapters/flask/test_live_helpers.py",
            "tests/adapters/django/test_live_helpers.py",
        ],
        [sys.executable, str(ROOT / "scripts" / "asset_audit.py")],
        [sys.executable, str(ROOT / "scripts" / "build_evidence_bundle.py")],
    ]
    for command in commands:
        print("+", *command)
        subprocess.check_call(command, cwd=ROOT)
    print("ok: PKG-011 local packaging evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
