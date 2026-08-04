#!/usr/bin/env python3
"""Fail if first-party HDN runtime paths remain outside CHANGELOG history."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Built from fragments so this file does not match its own search pattern.
PATTERN = re.compile(
    "|".join(
        [
            "hedron_core" + r"\.hdn",
            "compile" + "_hdn",
            "format" + "_hdn",
            "load" + "_hdn_program",
            "run" + "_program",
            "Render" + "Program",
            "HDN_" + "FORMAT_VERSION",
            "template" + r"\.hdn",
        ]
    )
)
SELF = Path(__file__).resolve()


def main() -> int:
    hits: list[str] = []
    for root_name in ("packages", "examples", "tests", "scripts"):
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.resolve() == SELF:
                continue
            if path.name == "CHANGELOG.md" or "CHANGELOG.md" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for line_no, line in enumerate(text.splitlines(), start=1):
                if PATTERN.search(line):
                    hits.append(f"{path.relative_to(ROOT)}:{line_no}:{line.strip()}")
    if hits:
        print("\n".join(hits), file=sys.stderr)
        return 1
    print("ok: no first-party HDN runtime paths remain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
