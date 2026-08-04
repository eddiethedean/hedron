#!/usr/bin/env python3
"""Sync root STATUS.md / ROADMAP.md from the MkDocs-canonical docs/ copies.

Docs links are rewritten with a ``docs/`` prefix so GitHub browsing from the
repository root resolves. Run after editing ``docs/STATUS.md`` or ``docs/ROADMAP.md``:

    uv run python scripts/sync_status_roadmap.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

# Rewrite markdown links that target same-tree docs paths for root consumers.
_LINK = re.compile(r"\]\((?!https?://|mailto:|#|docs/)([^)]+)\)")


def _to_root(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        target = match.group(1)
        if target.startswith(("acceptance/", "api/", "guides/", "rfcs/", "foundations/")):
            return f"](docs/{target})"
        if target.endswith(".md") and "/" not in target.split("#", 1)[0]:
            return f"](docs/{target})"
        if target.startswith("../"):
            return f"](docs/{target[3:]})"
        return match.group(0)

    return _LINK.sub(repl, text)


def main() -> None:
    for name in ("STATUS.md", "ROADMAP.md"):
        src = DOCS / name
        dst = ROOT / name
        body = src.read_text(encoding="utf-8")
        banner = (
            "<!-- Generated from docs/%s — edit the docs/ copy, then run "
            "scripts/sync_status_roadmap.py -->\n\n" % name
        )
        # Strip a previous banner if re-running.
        if body.startswith("<!-- Generated from docs/"):
            body = body.split("\n\n", 1)[1]
        dst.write_text(banner + _to_root(body), encoding="utf-8")
        print(f"wrote {dst.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
