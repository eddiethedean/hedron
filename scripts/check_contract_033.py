#!/usr/bin/env python3
"""CONTRACT-033: RFC Accepted, cut matrix, probe, bridge decision agreement."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_033 import (  # noqa: E402
    FIXTURES,
    PROBE_RESULT,
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
            PROBE_RESULT,
            ROOT / "docs" / "implementation" / "HEDRON_POSIT_033.md",
            ROOT / "docs" / "acceptance" / "release-gate-0.33.toml",
            ROOT / "docs" / "acceptance" / "production-grade-inventory-033.toml",
            ROOT / "docs" / "acceptance" / "upgrade-fixtures-033.md",
            ROOT / "docs" / "acceptance" / "security-review-033" / "BRIEF.md",
        ],
        errors,
    )
    require_dirs([FIXTURES], errors)
    require_inventory_packages(("hedron-posit", "hedron-workbench"), errors)
    if not rfc_is_accepted():
        errors.append("RFC-0066 must be Accepted before CONTRACT-033 can pass")
    if cut_matrix_has_tbd():
        errors.append("RELEASE_0_33 Exact cut matrix still contains TBD")
    if PROBE_RESULT.is_file():
        text = PROBE_RESULT.read_text(encoding="utf-8")
        if "RESULT=pass" not in text:
            errors.append("realconnect-033 RESULT.log does not record RESULT=pass")
        if "BRIDGE_DECISION=" not in text:
            errors.append("realconnect-033 RESULT.log missing BRIDGE_DECISION=")
    if fail_errors(errors, "CONTRACT-033"):
        return 1
    print("ok: CONTRACT-033")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
