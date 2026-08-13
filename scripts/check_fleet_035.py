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
)


def main() -> int:
    errors: list[str] = []
    require_files([RFC, RELEASE_PACKET, IMPLEMENTATION, GATE, INVENTORY, REVIEW_BRIEF], errors)
    require_inventory_shape(errors)
    text = INVENTORY.read_text(encoding="utf-8") if INVENTORY.is_file() else ""
    if "present_034_status" not in text:
        errors.append("inventory must record present_034_status")
    if fail_errors(errors, "FLEET-035"):
        return 1
    print("ok: FLEET-035 (packet refine shape)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
