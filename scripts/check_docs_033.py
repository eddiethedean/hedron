#!/usr/bin/env python3
"""DOCS-033: Posit docs packet presence (refine stub)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_033 import fail_errors, require_files  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "docs" / "acceptance" / "RELEASE_0_33.md",
            ROOT / "docs" / "rfcs" / "RFC-0066-HEDRON-POSIT.md",
            ROOT / "docs" / "guides" / "posit-workbench.md",
            ROOT / "docs" / "implementation" / "HEDRON_POSIT_033.md",
        ],
        errors,
    )
    # Full docs/guides/posit.md is Stage 4; outline stub may appear earlier.
    posit_guide = ROOT / "docs" / "guides" / "posit.md"
    if not posit_guide.is_file():
        print(
            "DOCS-033: docs/guides/posit.md not present yet (allowed at refine)",
            file=sys.stderr,
        )
    if fail_errors(errors, "DOCS-033"):
        return 1
    print("ok: DOCS-033")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
