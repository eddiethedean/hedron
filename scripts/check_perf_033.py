#!/usr/bin/env python3
"""PERF-033: locked p95 ceilings documented (refine stub)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_033 import fail_errors, require_files  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files([ROOT / "docs" / "acceptance" / "RELEASE_0_33.md"], errors)
    text = (ROOT / "docs" / "acceptance" / "RELEASE_0_33.md").read_text(encoding="utf-8")
    for needle in ("<=5 ms", "<=10 ms"):
        if needle not in text:
            errors.append(f"RELEASE_0_33 missing perf ceiling language {needle!r}")
    if fail_errors(errors, "PERF-033"):
        return 1
    print("ok: PERF-033")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
