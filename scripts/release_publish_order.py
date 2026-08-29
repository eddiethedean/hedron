#!/usr/bin/env python3
"""Validate and print the deterministic PyPI publication order."""

from __future__ import annotations

import sys
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
ORDER_PATH = ROOT / "release" / "publish-order.toml"


def main() -> int:
    data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    order = data.get("order")
    excluded = data.get("excluded")
    if not isinstance(order, list) or not all(isinstance(item, str) for item in order):
        raise SystemExit("release publish order must contain a string order list")
    if not isinstance(excluded, list) or not all(isinstance(item, str) for item in excluded):
        raise SystemExit("release publish order must contain a string excluded list")
    if len(order) != len(set(order)) or set(order) & set(excluded):
        raise SystemExit("release publish order contains duplicates or excluded projects")

    workspace_projects: set[str] = set()
    for project_file in sorted((ROOT / "packages").glob("*/pyproject.toml")):
        project = tomllib.loads(project_file.read_text(encoding="utf-8"))["project"]
        workspace_projects.add(str(project["name"]))
    missing = workspace_projects - set(order) - set(excluded)
    if missing:
        raise SystemExit(
            "release publish order does not classify workspace projects: "
            + ", ".join(sorted(missing))
        )
    for name in order:
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
