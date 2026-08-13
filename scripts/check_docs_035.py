#!/usr/bin/env python3
"""DOCS-035: Stage 0 docs packet presence (strict MkDocs reconcile at later stages)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_035 import (  # noqa: E402
    IMPLEMENTATION,
    RELEASE_PACKET,
    RFC,
    fail_errors,
    require_files,
)


def main() -> int:
    errors: list[str] = []
    require_files([RFC, RELEASE_PACKET, IMPLEMENTATION], errors)
    release = RELEASE_PACKET.read_text(encoding="utf-8") if RELEASE_PACKET.is_file() else ""
    if "PRESENT-034" not in release and "presentation" not in release.lower():
        errors.append("RELEASE_0_35 must mention PRESENT-034 / presentation fold-in")
    if fail_errors(errors, "DOCS-035"):
        return 1
    print("ok: DOCS-035 (packet refine stub)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
