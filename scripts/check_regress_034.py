#!/usr/bin/env python3
"""REGRESS-034: Gradio corpora and docs strict build."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_034 import fail_errors, require_files, run_pytest  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "docs" / "acceptance" / "release-gate-0.34.toml",
            ROOT / "docs" / "acceptance" / "production-grade-inventory-034.toml",
        ],
        errors,
    )
    if fail_errors(errors, "REGRESS-034"):
        return 1
    code = run_pytest(
        [
            "tests/unit/test_phase18_gradio.py",
            "tests/unit/test_gradio_034.py",
            "tests/security/test_gradio_034_adversarial.py",
            "tests/upgrade/test_0_33_to_0_34_gradio.py",
        ],
        "REGRESS-034",
    )
    if code != 0:
        return code
    cmd = [
        "uv",
        "run",
        "--group",
        "docs",
        "mkdocs",
        "build",
        "--strict",
        "-f",
        str(ROOT / "mkdocs.yml"),
    ]
    print("+", *cmd)
    try:
        subprocess.check_call(cmd, cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        print(f"REGRESS-034 mkdocs failed ({exc.returncode})", file=sys.stderr)
        return 1
    print("ok: REGRESS-034")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
