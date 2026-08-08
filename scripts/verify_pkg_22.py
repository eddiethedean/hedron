#!/usr/bin/env python3
"""Verify phase 0.22 packaging / packet evidence for CSRF composition.

Does **not** publish or tag. Requires Beta packages at ``0.22.0`` and Verified
rows in ``docs/acceptance/release-gate-0.22.toml``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FOCUSED_TESTS = [
    "tests/security/test_csrf.py",
    "tests/unit/test_phase22_csrf_strategies.py",
    "tests/unit/test_phase22_security_headers.py",
    "tests/unit/test_phase22_csrf_field_form.py",
    "tests/adapters/test_phase20_security_headers.py",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)

    commands = [
        [
            sys.executable,
            str(ROOT / "scripts" / "check_release_gate.py"),
            "0.22.0",
        ],
        [sys.executable, "-m", "pytest", "-q", *FOCUSED_TESTS],
    ]
    for command in commands:
        print("+", *command)
        subprocess.check_call(command, cwd=ROOT)
    print("ok: PKG-022 packaging / packet evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
