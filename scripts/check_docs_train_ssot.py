#!/usr/bin/env python3
"""Fail if adopter-facing docs claim a stale published train or banned maturity jargon.

The living line is 0.18.x. Historical whats-new / acceptance / RFC phase labels
are allowed. This check targets pages that assert "current" product maturity.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Paths that must not assert 0.16.x or 0.17.x as the *current* line.
CHECKED = [
    ROOT / "docs" / "SECURITY.md",
    ROOT / "SECURITY.md",
    ROOT / "docs" / "getting-started" / "installation.md",
    ROOT / "docs" / "guides" / "troubleshooting.md",
    ROOT / "docs" / "guides" / "faq.md",
    ROOT / "docs" / "guides" / "evidence-pack.md",
    ROOT / "docs" / "examples" / "try-it.md",
    ROOT / "docs" / "guides" / "best-practices.md",
    ROOT / "docs" / "guides" / "whats-ready.md",
    ROOT / "docs" / "guides" / "evaluate.md",
    ROOT / "docs" / "guides" / "upgrade.md",
    ROOT / "docs" / "getting-started" / "how-to-read.md",
    ROOT / "README.md",
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

# Adopter-facing jargon / maturity collisions banned on checked entry pages.
# Historical whats-new / RFCs are not in CHECKED.
BANNED = [
    re.compile(r"Supported beta", re.I),
    re.compile(r"Maturity SSOT"),
    re.compile(r"beachhead Supported", re.I),
    re.compile(r"as Supported beachhead", re.I),
    re.compile(r"Still Deferred \(after"),
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
        for pattern in BANNED:
            if pattern.search(text):
                failures.append(f"{path.relative_to(ROOT)}: banned {pattern.pattern}")
    if failures:
        print("stale or banned adopter-doc claims:", file=sys.stderr)
        for item in failures:
            print(f"  {item}", file=sys.stderr)
        return 1
    print(
        "ok: adopter docs assert 0.18 and avoid Supported beta / SSOT / beachhead jargon"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
