#!/usr/bin/env python3
"""Fail if a release tag is not ready for public publication."""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="Package version without the leading v")
    args = parser.parse_args()
    tag_version: str = args.version
    errors: list[str] = []

    if not (ROOT / "LICENSE").is_file():
        errors.append("missing root LICENSE (required before public publication)")

    for pyproject in sorted((ROOT / "packages").glob("*/pyproject.toml")):
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        project = data["project"]
        name = str(project["name"])
        version = str(project["version"])
        if version != tag_version:
            errors.append(f"{name}: package version {version!r} != tag {tag_version!r}")
        if "license" not in project and "license-files" not in project:
            errors.append(f"{name}: [project].license (or license-files) is required")
        pkg_dir = pyproject.parent
        init = next(pkg_dir.glob("src/*/__init__.py"))
        init_text = init.read_text(encoding="utf-8")
        match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', init_text, re.M)
        if not match:
            errors.append(f"{name}: __version__ not found in {init}")
        elif match.group(1) != tag_version:
            errors.append(f"{name}: __version__ {match.group(1)!r} != tag {tag_version!r}")
        changelog = pkg_dir / "CHANGELOG.md"
        if not changelog.is_file():
            errors.append(f"{name}: missing CHANGELOG.md")
        elif f"[{tag_version}]" not in changelog.read_text(encoding="utf-8"):
            errors.append(f"{name}: CHANGELOG.md lacks [{tag_version}] section")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"ok: release gate for {tag_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
