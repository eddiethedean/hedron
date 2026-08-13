#!/usr/bin/env python3
"""CONNECT-033: licensed native Connect matrix (refine: probe artifacts present)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_033 import (  # noqa: E402
    FIXTURES,
    PROBE_RESULT,
    fail_errors,
    require_dirs,
    require_files,
    require_inventory_keys,
)


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            PROBE_RESULT,
            ROOT / "docs" / "acceptance" / "CONNECT_PROBE_033.md",
            ROOT / "examples" / "connect-reference" / "app.py",
        ],
        errors,
    )
    require_dirs([FIXTURES], errors)
    require_inventory_keys(
        "hedron-posit",
        supported=("native_connect",),
        experimental=("off_host_connect",),
        errors=errors,
    )
    if PROBE_RESULT.is_file() and "NATIVE_COOKIES=ok" not in PROBE_RESULT.read_text(
        encoding="utf-8"
    ):
        errors.append("realconnect-033 RESULT.log missing NATIVE_COOKIES=ok")
    if fail_errors(errors, "CONNECT-033"):
        return 1
    print("ok: CONNECT-033")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
