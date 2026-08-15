#!/usr/bin/env python3
"""Sync root STATUS.md / ROADMAP.md and the public roadmap page from docs/.

``docs/STATUS.md`` and ``docs/ROADMAP.md`` are the single source of truth. Root
mirrors are generated for GitHub browsing. The public Read the Docs page
``docs/guides/roadmap.md`` is generated from the ``ADOPTER_ROADMAP`` marked
section inside ``docs/ROADMAP.md`` (MkDocs cannot publish the full maintainer
roadmap because it links into excluded RFCs/acceptance/implementation trees).

Run after editing the docs copies:

    uv run python scripts/sync_status_roadmap.py

CI / pre-push check (exit 1 if generated files are stale):

    uv run python scripts/sync_status_roadmap.py --check
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PUBLIC_ROADMAP = DOCS / "guides" / "roadmap.md"

# Rewrite markdown links that target same-tree docs paths for root consumers.
_LINK = re.compile(r"\]\((?!https?://|mailto:|#|docs/)([^)]+)\)")
_ADOPTER_BLOCK = re.compile(
    r"<!--\s*ADOPTER_ROADMAP_BEGIN\s*-->\n(.*)\n<!--\s*ADOPTER_ROADMAP_END\s*-->",
    re.DOTALL,
)


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


def _to_guides(text: str) -> str:
    """Rewrite docs/-root relative links for a page living under docs/guides/."""

    def repl(match: re.Match[str]) -> str:
        target = match.group(1)
        path, sep, frag = target.partition("#")
        suffix = f"{sep}{frag}" if sep else ""
        if path.startswith("guides/"):
            return f"]({path[len('guides/') :]}{suffix})"
        if path.startswith(("api/", "acceptance/", "rfcs/", "foundations/", "implementation/")):
            return f"](../{path}{suffix})"
        if path.endswith(".md") and "/" not in path:
            return f"](../{path}{suffix})"
        return match.group(0)

    return _LINK.sub(repl, text)


def _expected_root(name: str) -> str:
    src = DOCS / name
    body = src.read_text(encoding="utf-8")
    banner = (
        f"<!-- Generated from docs/{name} — edit the docs/ copy, then run "
        "scripts/sync_status_roadmap.py -->\n\n"
    )
    if body.startswith("<!-- Generated from docs/"):
        body = body.split("\n\n", 1)[1]
    return banner + _to_root(body)


def _adopter_section() -> str:
    body = (DOCS / "ROADMAP.md").read_text(encoding="utf-8")
    match = _ADOPTER_BLOCK.search(body)
    if not match:
        raise SystemExit(
            "docs/ROADMAP.md missing <!-- ADOPTER_ROADMAP_BEGIN/END --> markers "
            "for the public roadmap excerpt"
        )
    return match.group(1).strip() + "\n"


def _expected_public_roadmap() -> str:
    section = _to_guides(_adopter_section())
    # Public page title; section body already starts with prose (not an H1).
    return (
        "<!-- Generated from docs/ROADMAP.md ADOPTER_ROADMAP section — "
        "edit docs/ROADMAP.md, then run scripts/sync_status_roadmap.py -->\n\n"
        "# Roadmap\n\n"
        + section
        + "\nMaintainer phase tables, gates, and RFC ownership continue below the adopter "
        "summary in [`docs/ROADMAP.md`](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md) "
        "(root `ROADMAP.md` is a generated mirror of that file).\n"
    )


def sync() -> None:
    for name in ("STATUS.md", "ROADMAP.md"):
        dst = ROOT / name
        dst.write_text(_expected_root(name), encoding="utf-8")
        print(f"wrote {dst.relative_to(ROOT)}")
    PUBLIC_ROADMAP.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_ROADMAP.write_text(_expected_public_roadmap(), encoding="utf-8")
    print(f"wrote {PUBLIC_ROADMAP.relative_to(ROOT)}")


def check() -> int:
    stale: list[str] = []
    for name in ("STATUS.md", "ROADMAP.md"):
        dst = ROOT / name
        expected = _expected_root(name)
        actual = dst.read_text(encoding="utf-8") if dst.exists() else ""
        if actual != expected:
            stale.append(name)
    expected_public = _expected_public_roadmap()
    actual_public = PUBLIC_ROADMAP.read_text(encoding="utf-8") if PUBLIC_ROADMAP.exists() else ""
    if actual_public != expected_public:
        stale.append("docs/guides/roadmap.md")
    if stale:
        print(
            "Generated roadmap/status files are stale: "
            + ", ".join(stale)
            + "\nRun: uv run python scripts/sync_status_roadmap.py",
            file=sys.stderr,
        )
        return 1
    print("ok: root STATUS.md / ROADMAP.md and docs/guides/roadmap.md match docs/")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if generated files do not match docs/ (do not write)",
    )
    args = parser.parse_args()
    raise SystemExit(check() if args.check else sync() or 0)


if __name__ == "__main__":
    main()
