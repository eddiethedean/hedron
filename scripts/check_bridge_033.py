#!/usr/bin/env python3
"""BRIDGE-033: Supported bridge keep/drop decision from Stage 0."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_033 import (  # noqa: E402
    PROBE_RESULT,
    fail_errors,
    require_files,
    require_inventory_keys,
)


def main() -> int:
    errors: list[str] = []
    require_files([PROBE_RESULT], errors)
    if not PROBE_RESULT.is_file():
        return fail_errors(errors, "BRIDGE-033") or 1
    text = PROBE_RESULT.read_text(encoding="utf-8")
    if "BRIDGE_DECISION=drop_supported" in text:
        require_inventory_keys(
            "hedron-posit",
            experimental=("authenticated_header_v1_extension_point",),
            excluded=("authenticated_header_v1_supported",),
            errors=errors,
        )
    elif "BRIDGE_DECISION=keep_supported" in text:
        require_inventory_keys(
            "hedron-posit",
            supported=("authenticated_header_v1_supported",),
            errors=errors,
        )
    else:
        errors.append(
            "BRIDGE_DECISION must be keep_supported or drop_supported in RESULT.log"
        )
    if fail_errors(errors, "BRIDGE-033"):
        return 1
    print("ok: BRIDGE-033")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
