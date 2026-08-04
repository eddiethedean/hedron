#!/usr/bin/env python3
"""Verify phase 0.9 packaging evidence that can run without a public index."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    commands = [
        [sys.executable, "-m", "pytest", "-q", "tests/upgrade/test_0_8_to_0_9_authoring.py"],
        [sys.executable, "-m", "pytest", "-q", "tests/jinja/test_progressive_example.py"],
        [sys.executable, str(ROOT / "scripts" / "build_evidence_bundle.py")],
    ]
    for command in commands:
        print("+", *command)
        subprocess.check_call(command, cwd=ROOT)
    print("ok: PKG-09-001 local packaging evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
