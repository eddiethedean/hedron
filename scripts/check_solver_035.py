#!/usr/bin/env python3
"""SOLVER-035: Supported extras, upgrade fixtures, and mixed-version honesty."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_035 import (  # noqa: E402
    IMPLEMENTATION,
    RELEASE_PACKET,
    UPGRADE_FIXTURES,
    fail_errors,
    require_files,
    run_pytest,
)


def main() -> int:
    errors: list[str] = []
    require_files([RELEASE_PACKET, IMPLEMENTATION, UPGRADE_FIXTURES], errors)
    text = UPGRADE_FIXTURES.read_text(encoding="utf-8") if UPGRADE_FIXTURES.is_file() else ""
    for needle in ("v0.34.0", "v0.35.0", "0.25", "offline", "mixed-version"):
        if needle not in text:
            errors.append(f"upgrade-fixtures-035.md missing {needle!r}")
    if fail_errors(errors, "SOLVER-035"):
        return 1
    if run_pytest(
        [
            "tests/ops/test_solver_035.py",
            "tests/upgrade/test_0_34_to_0_35_fleet.py",
        ],
        "SOLVER-035",
    ):
        return 1
    print("ok: SOLVER-035")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
