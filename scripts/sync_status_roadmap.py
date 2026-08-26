#!/usr/bin/env python3
"""Sync root STATUS.md from the docs/-canonical copy.

``docs/STATUS.md`` is the single source of truth for project status. Root
``STATUS.md`` is generated for GitHub browsing.

The capability roadmap lives in exactly one file: ``docs/ROADMAP.md`` (no root
mirror, no generated guides page).

Run after editing ``docs/STATUS.md``:

    uv run python scripts/sync_status_roadmap.py

CI / pre-push check (exit 1 if root STATUS.md is stale, or if forbidden
roadmap duplicates exist):

    uv run python scripts/sync_status_roadmap.py --check
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
FORBIDDEN_ROADMAPS = (
    ROOT / "ROADMAP.md",
    DOCS / "guides" / "roadmap.md",
)

# Rewrite markdown links that target same-tree docs paths for root consumers.
_LINK = re.compile(r"\]\((?!https?://|mailto:|#|docs/)([^)]+)\)")


def _to_root(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        target = match.group(1)
        if target.startswith(
            ("acceptance/", "api/", "guides/", "rfcs/", "foundations/", "implementation/")
        ):
            return f"](docs/{target})"
        if target.endswith(".md") and "/" not in target.split("#", 1)[0]:
            return f"](docs/{target})"
        if target.startswith("../"):
            return f"](docs/{target[3:]})"
        return match.group(0)

    return _LINK.sub(repl, text)


def _expected_root_status() -> str:
    src = DOCS / "STATUS.md"
    body = src.read_text(encoding="utf-8")
    banner = (
        "<!-- Generated from docs/STATUS.md — edit the docs/ copy, then run "
        "scripts/sync_status_roadmap.py -->\n\n"
    )
    if body.startswith("<!-- Generated from docs/"):
        body = body.split("\n\n", 1)[1]
    return banner + _to_root(body)


def _forbidden_roadmap_errors() -> list[str]:
    errors: list[str] = []
    for path in FORBIDDEN_ROADMAPS:
        if path.exists():
            errors.append(
                f"forbidden roadmap duplicate: {path.relative_to(ROOT)} "
                "(only docs/ROADMAP.md is allowed)"
            )
    return errors


def sync() -> None:
    for path in FORBIDDEN_ROADMAPS:
        if path.exists():
            path.unlink()
            print(f"removed {path.relative_to(ROOT)}")
    dst = ROOT / "STATUS.md"
    dst.write_text(_expected_root_status(), encoding="utf-8")
    print(f"wrote {dst.relative_to(ROOT)}")


def check() -> int:
    stale: list[str] = []
    dst = ROOT / "STATUS.md"
    expected = _expected_root_status()
    actual = dst.read_text(encoding="utf-8") if dst.exists() else ""
    if actual != expected:
        stale.append("STATUS.md")
    errors = _forbidden_roadmap_errors()
    if stale:
        print(
            "Root STATUS.md mirror is stale: "
            + ", ".join(stale)
            + "\nRun: uv run python scripts/sync_status_roadmap.py",
            file=sys.stderr,
        )
    if errors:
        print("\n".join(errors), file=sys.stderr)
    if stale or errors:
        return 1
    print("ok: root STATUS.md matches docs/; canonical Hedron roadmap is docs/ROADMAP.md")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if root STATUS.md is stale or forbidden roadmap files exist",
    )
    args = parser.parse_args()
    raise SystemExit(check() if args.check else sync() or 0)


if __name__ == "__main__":
    main()
