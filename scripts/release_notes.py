#!/usr/bin/env python3
"""Print the changelog body for a release version."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="Package version without the leading v")
    parser.add_argument(
        "--package",
        default="hedron-core",
        help="Workspace package directory name (default: hedron-core)",
    )
    args = parser.parse_args()
    changelog = ROOT / "packages" / args.package / "CHANGELOG.md"
    text = changelog.read_text(encoding="utf-8")
    pattern = rf"## \[{re.escape(args.version)}\].*?\n(.*?)(?=\n## \[|\Z)"
    match = re.search(pattern, text, re.S)
    body = match.group(1).strip() if match else f"{args.package} {args.version}"
    print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
