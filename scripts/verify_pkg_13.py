#!/usr/bin/env python3
"""Verify phase 0.13 packaging evidence that can run without a public index."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GATE_TESTS = [
    "tests/unit/test_prepare_lifecycle.py",
    "tests/unit/test_async_scenario_harness.py",
    "tests/unit/test_adaptive_concurrency.py",
    "tests/unit/test_distributed_tracing.py",
    "tests/jinja/test_hdj_async_io.py",
    "tests/unit/test_security_audit_sink.py",
    "tests/conformance/test_celery_rq_durable.py",
    "tests/conformance/test_live_claim_honesty.py",
    "tests/performance/test_async_scenarios.py",
]


def _assert_extras_pins() -> None:
    text = (ROOT / "packages/hedron/pyproject.toml").read_text(encoding="utf-8")
    for extra, pattern in (
        ("dev", r"hedron-explorer>=0\.13\.0,<0\.14"),
        ("jinja", r"hedron-jinja>=0\.13\.0,<0\.14"),
        ("otel", r"opentelemetry-api>=1\.27,<2"),
    ):
        if not re.search(pattern, text):
            raise SystemExit(f"hedron[{extra}] pin must match {pattern}")


def main() -> int:
    _assert_extras_pins()
    commands = [
        [sys.executable, "-m", "pytest", "-q", *GATE_TESTS],
        [sys.executable, str(ROOT / "scripts" / "check_hed_codes.py")],
        [
            sys.executable,
            str(ROOT / "scripts" / "check_release_gate.py"),
            "0.13.0",
            "--skip-evidence",
        ],
    ]
    for command in commands:
        print("+", *command)
        subprocess.check_call(command, cwd=ROOT)
    print("ok: PKG-013 local packaging evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
