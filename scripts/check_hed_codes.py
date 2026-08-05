#!/usr/bin/env python3
"""Fail when packages emit unregistered HED-* diagnostic codes."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE_RE = re.compile(r"HED-[A-Z]+-\d+")
PACKAGES = ROOT / "packages"


def main() -> int:
    sys.path.insert(0, str(ROOT / "packages" / "hedron-core" / "src"))
    from hedron_core.codes import ALL_CODES

    emitted: set[str] = set()
    for path in PACKAGES.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        emitted.update(CODE_RE.findall(text))

    missing = sorted(emitted - set(ALL_CODES))
    if missing:
        print("Unregistered HED-* codes:", file=sys.stderr)
        for code in missing:
            print(f"  {code}", file=sys.stderr)
        return 1
    print(f"ok: {len(emitted)} emitted codes registered ({len(ALL_CODES)} catalog entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
