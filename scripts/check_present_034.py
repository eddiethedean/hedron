#!/usr/bin/env python3
"""PRESENT-034: optional default presentation gate (deferred to 0.35)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "implementation" / "DEFAULT_PRESENTATION_033_PLUS.md"


def main() -> int:
    if not PLAN.is_file():
        print("PRESENT-034: missing presentation plan", file=sys.stderr)
        return 1
    text = PLAN.read_text(encoding="utf-8")
    if "0.34" not in text or "gallery" not in text.lower():
        print("PRESENT-034: presentation plan incomplete", file=sys.stderr)
        return 1
    print("ok: PRESENT-034 deferred (gallery not required for Gradio-first 0.34 cut)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
