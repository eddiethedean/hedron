#!/usr/bin/env python3
"""SECURITY-030: adversarial suite + review packet."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_030 import require_files, run_pytest, workbench_pytest_paths  # noqa: E402

REVIEW = ROOT / "docs" / "acceptance" / "security-review-030"


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            REVIEW / "BRIEF.md",
            REVIEW / "REDACTED_REPORT.md",
            REVIEW / "DISPOSITION.toml",
            ROOT / "tests" / "security" / "test_workbench_adversarial.py",
        ],
        errors,
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    disposition = tomllib.loads((REVIEW / "DISPOSITION.toml").read_text(encoding="utf-8"))
    if disposition.get("critical_high_open") is not False:
        print("DISPOSITION.toml critical_high_open must be false", file=sys.stderr)
        return 1
    paths = ["tests/security/test_workbench_adversarial.py", *workbench_pytest_paths()]
    if run_pytest(list(dict.fromkeys(paths)), "SECURITY-030"):
        return 1
    print("ok: SECURITY-030")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
