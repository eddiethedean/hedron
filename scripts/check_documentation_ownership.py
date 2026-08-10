#!/usr/bin/env python3
"""Validate that every published Markdown page has an owner and review cadence."""

from __future__ import annotations

import fnmatch
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CONFIG = DOCS / "documentation.toml"


def _matches(path: str, pattern: str) -> bool:
    # pathlib-style ``**`` is not consistently handled by fnmatch for a file at
    # the pattern root, so accept both the exact prefix and the glob.
    if pattern.endswith("/**") and path.startswith(pattern[:-3] + "/"):
        return True
    if "/" not in pattern and "/" in path:
        return False
    return fnmatch.fnmatchcase(path, pattern)


def main() -> int:
    data = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    groups = data.get("group", [])
    problems: list[str] = []

    for group in groups:
        for field in ("name", "patterns", "owner", "review"):
            if not group.get(field):
                problems.append(f"documentation.toml: group missing {field!r}")

    excluded_roots = {"archive", "rfcs", "acceptance", "implementation", "overrides"}
    for path in sorted(DOCS.rglob("*.md")):
        relative = path.relative_to(DOCS).as_posix()
        if relative.split("/", 1)[0] in excluded_roots:
            continue
        owners = [
            group["name"]
            for group in groups
            if any(_matches(relative, pattern) for pattern in group["patterns"])
        ]
        if len(owners) != 1:
            problems.append(
                f"{relative}: expected one documentation owner, found "
                f"{', '.join(owners) if owners else 'none'}"
            )

    if problems:
        raise SystemExit("\n".join(problems))
    print(f"ok: {len(groups)} documentation ownership groups cover published Markdown")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
