#!/usr/bin/env python3
"""Generate the public example catalog from ``examples/catalog.toml``."""

from __future__ import annotations

import argparse
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "catalog.toml"
OUTPUT = ROOT / "docs" / "examples" / "catalog.md"


def render() -> str:
    entries = tomllib.loads(SOURCE.read_text(encoding="utf-8"))["example"]
    paths = {entry["path"] for entry in entries}
    directories = {path.name for path in (ROOT / "examples").iterdir() if path.is_dir()}
    missing = sorted(directories - paths)
    unknown = sorted(paths - directories)
    if missing or unknown:
        raise ValueError(f"catalog mismatch: missing={missing}, unknown={unknown}")

    lines = [
        "---",
        "description: Generated catalog of runnable and historical repository examples.",
        "---",
        "",
        "# Repository example catalog",
        "",
        "Generated from `examples/catalog.toml`. Current examples target the 1.0 contract;",
        "historical examples are phase evidence and are not recommended starting points.",
        "",
        "| Example | Outcome | Layer | Difficulty | Time | Status |",
        "|---|---|---|---|---:|---|",
    ]
    for entry in sorted(entries, key=lambda item: (item["status"] != "current", item["path"])):
        path = entry["path"]
        url = f"https://github.com/eddiethedean/hedron/tree/v1.0/examples/{path}"
        duration = f'{entry["minutes"]} min' if entry["minutes"] else "—"
        lines.append(
            f'| [`{path}`]({url}) | {entry["outcome"]} | {entry["layer"]} | '
            f'{entry["difficulty"]} | {duration} | {entry["status"].title()} |'
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render()
    if args.check:
        actual = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if actual != expected:
            raise SystemExit(
                "docs/examples/catalog.md is stale; run "
                "uv run python scripts/generate_example_catalog.py"
            )
        print(f"ok: {OUTPUT.relative_to(ROOT)} matches examples/catalog.toml")
        return 0
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
