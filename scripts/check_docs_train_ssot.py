#!/usr/bin/env python3
"""Fail if adopter-facing docs claim a stale published train.

The living train is 0.18.x. Historical whats-new / acceptance / RFC phase labels
are allowed. This check targets pages that assert "current published train".
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Paths that must not assert 0.16.x or 0.17.x as the *current* train.
CHECKED = [
    ROOT / "docs" / "SECURITY.md",
    ROOT / "SECURITY.md",
    ROOT / "docs" / "getting-started" / "installation.md",
    ROOT / "docs" / "guides" / "troubleshooting.md",
    ROOT / "docs" / "guides" / "faq.md",
    ROOT / "docs" / "guides" / "evidence-pack.md",
    ROOT / "docs" / "examples" / "try-it.md",
    ROOT / "docs" / "guides" / "best-practices.md",
]

# Patterns that indicate stale "current train" claims (not historical mentions).
STALE = [
    re.compile(r"current published train[^\n]*0\.16", re.I),
    re.compile(r"current published train[^\n]*0\.17", re.I),
    re.compile(r"train is \*\*0\.16\.x\*\*", re.I),
    re.compile(r"latest published train is \*\*0\.16", re.I),
    re.compile(r"Expect \*\*`0\.17\.0`\*\*", re.I),
    re.compile(r"matching `0\.16\.x` pin", re.I),
    re.compile(r"hedron==0\.17\.0", re.I),
    re.compile(r"verify_pkg_15\.py", re.I),
    re.compile(r"hedron>=0\.17\.0", re.I),
    re.compile(r"capture UI remains Deferred", re.I),
    re.compile(r"Supported lines: \*\*`0\.16\.x`", re.I),
]


def main() -> int:
    failures: list[str] = []
    for path in CHECKED:
        if not path.is_file():
            failures.append(f"missing file: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in STALE:
            if pattern.search(text):
                failures.append(f"{path.relative_to(ROOT)}: matches {pattern.pattern}")
    if failures:
        print("stale current-train claims:", file=sys.stderr)
        for item in failures:
            print(f"  {item}", file=sys.stderr)
        return 1
    print("ok: adopter docs assert current train 0.18 (no stale 0.16/0.17 current claims)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
