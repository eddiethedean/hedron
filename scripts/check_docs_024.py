#!/usr/bin/env python3
"""DOCS-024: train-pin SSOT + live-claim honesty for phase 0.24.

Runs ``check_docs_train_ssot.py`` then the live-claim honesty pytest module via
``uv run`` so the workspace venv (not the caller interpreter) is used.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    uv = shutil.which("uv")
    if uv is None:
        print("uv is required to run DOCS-024 live-claim pytest", file=sys.stderr)
        return 1

    commands = [
        [sys.executable, str(ROOT / "scripts" / "check_docs_train_ssot.py")],
        [
            uv,
            "run",
            "pytest",
            "-q",
            str(ROOT / "tests" / "conformance" / "test_live_claim_honesty.py"),
        ],
    ]
    for cmd in commands:
        print("+", *cmd)
        subprocess.check_call(cmd, cwd=ROOT)
    print("ok: DOCS-024 train SSOT + live-claim honesty")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
