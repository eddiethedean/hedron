#!/usr/bin/env python3
"""Require PyPI-safe absolute links in package README files."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")


def main() -> int:
    problems: list[str] = []
    for path in sorted((ROOT / "packages").glob("*/README.md")):
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for target in LINK_PATTERN.findall(line):
                if target.startswith(("https://", "http://", "mailto:", "#")):
                    continue
                problems.append(
                    f"{path.relative_to(ROOT)}:{line_number}: relative PyPI link {target!r}"
                )
    if problems:
        raise SystemExit("\n".join(problems))
    print("ok: package README links are absolute and PyPI-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
