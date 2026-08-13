#!/usr/bin/env python3
"""CONTRACT-034: RFC Accepted, cut matrix, inventory, and probe agreement."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_034 import (  # noqa: E402
    FIXTURES,
    IMPLEMENTATION,
    PROBE_RUNBOOK,
    RELEASE_PACKET,
    RFC,
    cut_matrix_has_tbd,
    fail_errors,
    require_dirs,
    require_files,
    require_inventory_packages,
    rfc_is_accepted,
)


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            RFC,
            RELEASE_PACKET,
            PROBE_RUNBOOK,
            IMPLEMENTATION,
            ROOT / "docs" / "acceptance" / "release-gate-0.34.toml",
            ROOT / "docs" / "acceptance" / "production-grade-inventory-034.toml",
            ROOT / "docs" / "acceptance" / "security-review-034" / "BRIEF.md",
        ],
        errors,
    )
    require_dirs([FIXTURES], errors)
    require_inventory_packages(("hedron-gradio",), errors)
    if not rfc_is_accepted():
        errors.append("RFC-0067 must be Accepted before CONTRACT-034 can pass")
    if cut_matrix_has_tbd():
        errors.append("RELEASE_0_34 Exact cut matrix still contains TBD")
    if fail_errors(errors, "CONTRACT-034"):
        return 1
    print("ok: CONTRACT-034")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
