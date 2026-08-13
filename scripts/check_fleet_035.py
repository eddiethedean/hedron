#!/usr/bin/env python3
"""FLEET-035: fleet inventory covers every package with owner + disposition."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_035 import (  # noqa: E402
    GATE,
    IMPLEMENTATION,
    INVENTORY,
    RELEASE_PACKET,
    REVIEW_BRIEF,
    RFC,
    fail_errors,
    require_files,
    require_inventory_shape,
    rfc_is_accepted,
    run_pytest,
)


def main() -> int:
    errors: list[str] = []
    require_files([RFC, RELEASE_PACKET, IMPLEMENTATION, GATE, INVENTORY, REVIEW_BRIEF], errors)
    require_inventory_shape(errors)
    if not rfc_is_accepted():
        errors.append("RFC-0068 must be Accepted before FLEET-035 can pass")
    if fail_errors(errors, "FLEET-035"):
        return 1
    if run_pytest(["tests/ops/test_fleet_035.py"], "FLEET-035"):
        return 1
    print("ok: FLEET-035")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
