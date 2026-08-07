#!/usr/bin/env python3
"""Verify phase 0.10 packaging evidence that can run without a public index."""

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
            "tests/unit/test_sse.py",
            "tests/unit/test_streaming.py",
        ],
        [sys.executable, "-m", "pytest", "-q", "tests/jinja/test_live_head_stream_htmx.py"],
        [sys.executable, str(ROOT / "scripts" / "asset_audit.py")],
        [sys.executable, str(ROOT / "scripts" / "build_evidence_bundle.py")],
    ]
    for command in commands:
        print("+", *command)
        subprocess.check_call(command, cwd=ROOT)
    print("ok: PKG-10-001 local packaging evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
