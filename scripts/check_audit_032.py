#!/usr/bin/env python3
"""AUDIT-032: redacted structured audit evidence."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_032 import (  # noqa: E402
    fail_errors,
    require_files,
    require_inventory_supported,
    run_pytest,
)


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "packages" / "hedron-mcp" / "src" / "hedron_mcp" / "audit.py",
            ROOT / "tests" / "unit" / "test_audit_032.py",
        ],
        errors,
    )
    require_inventory_supported(
        "hedron-mcp",
        ("redacted_structured_audit",),
        errors,
    )
    if fail_errors(errors, "AUDIT-032"):
        return 1
    return run_pytest(["tests/unit/test_audit_032.py"], "AUDIT-032")


if __name__ == "__main__":
    raise SystemExit(main())
