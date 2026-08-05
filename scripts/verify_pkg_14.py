#!/usr/bin/env python3
"""Verify phase 0.14 packaging evidence that can run without a public index."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GATE_TESTS = [
    "tests/unit/test_conformance_kit.py",
    "tests/unit/test_conformance_spec.py",
    "tests/unit/test_native_accel.py",
    "tests/unit/test_native_parity.py",
    "tests/jinja/test_hdj_instrumentation.py",
]


def _assert_extras_pins() -> None:
    text = (ROOT / "packages/hedron/pyproject.toml").read_text(encoding="utf-8")
    for extra, pattern in (
        ("dev", r"hedron-explorer>=0\.14\.0,<0\.15"),
        ("jinja", r"hedron-jinja>=0\.14\.0,<0\.15"),
        ("native", r"hedron-native>=0\.1\.0,<0\.2"),
        ("conformance", r"hedron-conformance>=0\.14\.0,<0\.15"),
    ):
        if not re.search(pattern, text):
            raise SystemExit(f"hedron[{extra}] pin must match {pattern}")


def main() -> int:
    _assert_extras_pins()
    commands = [
        [sys.executable, "-m", "pytest", "-q", *GATE_TESTS],
        ["node", str(ROOT / "packages/hedron-runtime-node/bin/run-conformance.mjs")],
        ["bash", str(ROOT / "packages/hedron-runtime-java/scripts/run-conformance.sh")],
        [sys.executable, str(ROOT / "scripts" / "check_release_gate.py"), "0.14.0", "--skip-evidence"],
    ]
    for command in commands:
        print("+", *command)
        subprocess.check_call(command, cwd=ROOT)
    print("ok: PKG-014 local packaging evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
