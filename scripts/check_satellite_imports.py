#!/usr/bin/env python3
"""Fail if core-only satellites import the FastAPI ``hedron`` package.

Packages that declare only ``hedron-core`` (or no Hedron flagship dependency) must not
import ``hedron`` / ``hedron.*``. Known interaction-helper debt is allowlisted until
handles/refresh protocols move into ``hedron-core`` (1.0 readiness). New violations fail CI.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# package dir name -> src import root relative to packages/<name>/src/
SATELLITES: dict[str, str] = {
    "hedron-data": "hedron_data",
    "hedron-charts": "hedron_charts",
    "hedron-maps": "hedron_maps",
    "hedron-extras": "hedron_extras",
    "hedron-elements": "hedron_elements",
    "hedron-sample-kit": "hedron_sample_kit",
    "hedron-conformance": "hedron_conformance",
    "hedron-native": "hedron_native",
}

# Known debt: interaction helpers that reach into FastAPI hedron (must shrink, not grow).
ALLOWED: frozenset[str] = frozenset(
    {
        "packages/hedron-data/src/hedron_data/workspace.py",
        "packages/hedron-charts/src/hedron_charts/interaction.py",
        "packages/hedron-maps/src/hedron_maps/interaction.py",
    }
)


def _imports_hedron_flagship(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "hedron" or alias.name.startswith("hedron."):
                    return True
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "hedron" or module.startswith("hedron."):
                return True
    return False


def main() -> int:
    errors: list[str] = []
    found_allowed: set[str] = set()
    for pkg, import_root in SATELLITES.items():
        src = ROOT / "packages" / pkg / "src" / import_root
        if not src.is_dir():
            errors.append(f"missing satellite src: {src.relative_to(ROOT)}")
            continue
        for path in sorted(src.rglob("*.py")):
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            if not _imports_hedron_flagship(path):
                continue
            if rel in ALLOWED:
                found_allowed.add(rel)
                continue
            errors.append(f"{rel} must not import FastAPI package 'hedron' (core-only satellite)")

    stale = sorted(ALLOWED - found_allowed)
    for rel in stale:
        errors.append(f"allowlist entry unused (remove from ALLOWED): {rel}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"ok: satellite→hedron import boundary ({len(ALLOWED)} allowlisted debt file(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
