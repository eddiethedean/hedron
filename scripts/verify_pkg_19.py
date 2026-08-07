#!/usr/bin/env python3
"""Verify phase 0.19 packaging evidence that can run without a public index."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GATE_TESTS = [
    "tests/unit/test_phase19_profile.py",
    "tests/unit/test_phase19_contract.py",
    "tests/unit/test_phase19_governance.py",
    "tests/unit/test_phase19_landmarks.py",
    "tests/unit/test_phase19_page_scripts.py",
    "tests/unit/test_phase19_atag.py",
    "tests/unit/test_phase19_explorer_a11y.py",
    "tests/a11y/test_phase19_interact.py",
    "tests/a11y/test_phase19_media.py",
    "tests/a11y/test_phase19_cognitive.py",
    "tests/a11y/test_phase19_i18n.py",
    "tests/a11y/test_phase19_scenario.py",
    "tests/integration/test_phase19_progressive_enhancement.py",
    "tests/browser/test_phase19_at_matrix.py",
]


def _assert_extras_pins() -> None:
    text = (ROOT / "packages/hedron/pyproject.toml").read_text(encoding="utf-8")
    for extra, pattern in (
        ("dev", r"hedron-explorer>=0\.19\.0,<0\.20"),
        ("jinja", r"hedron-jinja>=0\.19\.0,<0\.20"),
        ("native", r"hedron-native>=0\.1\.0,<0\.2"),
        ("conformance", r"hedron-conformance>=0\.19\.0,<0\.20"),
        ("extras", r"hedron-extras>=0\.19\.0,<0\.20"),
        ("notebook", r"hedron-notebook>=0\.1\.0,<0\.2"),
        ("mcp", r"hedron-mcp>=0\.1\.0,<0\.2"),
        ("gradio", r"hedron-gradio>=0\.1\.0,<0\.2"),
    ):
        if not re.search(pattern, text):
            raise SystemExit(f"hedron[{extra}] pin must match {pattern}")


def main() -> int:
    _assert_extras_pins()
    commands = [
        [sys.executable, "-m", "pytest", "-q", *GATE_TESTS],
        [
            sys.executable,
            str(ROOT / "scripts" / "check_release_gate.py"),
            "0.19.0",
            "--skip-evidence",
        ],
    ]
    for command in commands:
        print("+", *command)
        subprocess.check_call(command, cwd=ROOT)
    print("ok: PKG-019 local packaging evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
