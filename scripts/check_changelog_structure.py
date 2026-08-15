#!/usr/bin/env python3
"""Validate package changelog headings and release-section structure."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_HEADING = re.compile(r"^## \[([^\]]+)\](?: — (?:\d{4}-\d{2}-\d{2}|Unreleased))?$")


def check_changelog(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    failures: list[str] = []
    try:
        display = path.relative_to(ROOT)
    except ValueError:
        display = path
    first = next((line for line in lines if line.strip()), "")
    title_count = sum(line == "# Changelog" for line in lines)
    if first != "# Changelog":
        failures.append(f"{display}: first non-empty line must be '# Changelog'")
    if title_count != 1:
        failures.append(f"{display}: expected one '# Changelog' title; found {title_count}")

    headings = [
        (index, match.group(1))
        for index, line in enumerate(lines)
        if (match := RELEASE_HEADING.fullmatch(line))
    ]
    versions = [version for _, version in headings]
    duplicates = sorted({version for version in versions if versions.count(version) > 1})
    if duplicates:
        failures.append(f"{display}: duplicate release sections: {', '.join(duplicates)}")

    for position, (start, version) in enumerate(headings):
        end = headings[position + 1][0] if position + 1 < len(headings) else len(lines)
        body = [
            line for line in lines[start + 1 : end] if line.strip() and not line.startswith("#")
        ]
        if not body:
            failures.append(f"{display}: release [{version}] has no content")

    pyproject = path.with_name("pyproject.toml")
    if pyproject.is_file():
        current = str(tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]["version"])
        if current not in versions:
            failures.append(f"{display}: missing current package release [{current}]")
    return failures


def main() -> int:
    failures: list[str] = []
    paths = sorted((ROOT / "packages").glob("*/CHANGELOG.md"))
    catalog = (ROOT / "docs" / "guides" / "changelog.md").read_text(encoding="utf-8")
    for path in paths:
        failures.extend(check_changelog(path))
        package = path.parent.name
        if f"| `{package}` |" not in catalog:
            failures.append(
                f"docs/guides/changelog.md: missing package changelog entry for {package}"
            )
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"ok: {len(paths)} package changelogs have one title and non-empty releases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
