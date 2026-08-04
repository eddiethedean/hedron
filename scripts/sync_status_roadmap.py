#!/usr/bin/env python3
"""Sync root STATUS.md / ROADMAP.md from the docs/-canonical copies.

``docs/STATUS.md`` and ``docs/ROADMAP.md`` are the single source of truth. Root
mirrors are generated for GitHub browsing. Run after editing the docs copies:

    uv run python scripts/sync_status_roadmap.py

CI / pre-push check (exit 1 if root mirrors are stale):

    uv run python scripts/sync_status_roadmap.py --check
"""

from __future__ import annotations

import argparse
import re
import sys
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


def _expected_root(name: str) -> str:
    src = DOCS / name
    body = src.read_text(encoding="utf-8")
    banner = (
        "<!-- Generated from docs/%s — edit the docs/ copy, then run "
        "scripts/sync_status_roadmap.py -->\n\n" % name
    )
    if body.startswith("<!-- Generated from docs/"):
        body = body.split("\n\n", 1)[1]
    return banner + _to_root(body)


def sync() -> None:
    for name in ("STATUS.md", "ROADMAP.md"):
        dst = ROOT / name
        dst.write_text(_expected_root(name), encoding="utf-8")
        print(f"wrote {dst.relative_to(ROOT)}")


def check() -> int:
    stale: list[str] = []
    for name in ("STATUS.md", "ROADMAP.md"):
        dst = ROOT / name
        expected = _expected_root(name)
        actual = dst.read_text(encoding="utf-8") if dst.exists() else ""
        if actual != expected:
            stale.append(name)
    if stale:
        print(
            "Root STATUS/ROADMAP mirrors are stale: "
            + ", ".join(stale)
            + "\nRun: uv run python scripts/sync_status_roadmap.py",
            file=sys.stderr,
        )
        return 1
    print("ok: root STATUS.md / ROADMAP.md match docs/")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if root mirrors do not match docs/ (do not write)",
    )
    args = parser.parse_args()
    raise SystemExit(check() if args.check else sync() or 0)


if __name__ == "__main__":
    main()
