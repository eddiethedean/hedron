#!/usr/bin/env python3
"""Verify phase 0.21 packaging / packet evidence that can run without human AT sessions.

Does **not** bump package pins to 0.21 and does **not** require ``--require-sessions``.
Living Published train remains 0.20 until a real Verified human AT cut.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FOCUSED_TESTS = [
    "tests/unit/test_phase19_governance.py",
    "tests/integration/test_reference_crud.py",
    "tests/unit/test_human_at_packet.py",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)

    commands = [
        [sys.executable, str(ROOT / "scripts" / "check_human_at_packet.py")],
        [sys.executable, "-m", "pytest", "-q", *FOCUSED_TESTS],
        [
            sys.executable,
            str(ROOT / "scripts" / "check_release_gate.py"),
            "0.21.0",
            "--allow-planned",
        ],
    ]
    for command in commands:
        print("+", *command)
        subprocess.check_call(command, cwd=ROOT)
    print("ok: PKG-021 local packaging / packet evidence (sessions still Planned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
