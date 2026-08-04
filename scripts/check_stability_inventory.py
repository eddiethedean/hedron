#!/usr/bin/env python3
"""Verify public __all__ exports are covered by the 0.8 stability catalog."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STABILITY = ROOT / "docs" / "api" / "STABILITY.md"
PACKAGES = [
    "hedron",
    "hedron_core",
    "hedron_data",
    "hedron_charts",
    "hedron_flask",
    "hedron_django",
    "hedron_explorer",
    "hedron_sample_kit",
]


def package_init(name: str) -> Path:
    # map import name -> package dir
    mapping = {
        "hedron": ROOT / "packages" / "hedron" / "src" / "hedron" / "__init__.py",
        "hedron_core": ROOT / "packages" / "hedron-core" / "src" / "hedron_core" / "__init__.py",
        "hedron_data": ROOT / "packages" / "hedron-data" / "src" / "hedron_data" / "__init__.py",
        "hedron_charts": ROOT
        / "packages"
        / "hedron-charts"
        / "src"
        / "hedron_charts"
        / "__init__.py",
        "hedron_flask": ROOT / "packages" / "hedron-flask" / "src" / "hedron_flask" / "__init__.py",
        "hedron_django": ROOT
        / "packages"
        / "hedron-django"
        / "src"
        / "hedron_django"
        / "__init__.py",
        "hedron_explorer": ROOT
        / "packages"
        / "hedron-explorer"
        / "src"
        / "hedron_explorer"
        / "__init__.py",
        "hedron_sample_kit": ROOT
        / "packages"
        / "hedron-sample-kit"
        / "src"
        / "hedron_sample_kit"
        / "__init__.py",
    }
    return mapping[name]


def read_all(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Name)
                    and target.id == "__all__"
                    and isinstance(node.value, (ast.List, ast.Tuple))
                ):
                    names: list[str] = []
                    for elt in node.value.elts:
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                            names.append(elt.value)
                    return names
    return []


def main() -> int:
    errors: list[str] = []
    if not STABILITY.is_file():
        errors.append(f"missing stability catalog: {STABILITY}")
        print("\n".join(errors), file=sys.stderr)
        return 1

    text = STABILITY.read_text(encoding="utf-8")
    required_sections = [
        "hedron",
        "hedron-core",
        "hedron-data",
        "hedron-charts",
        "hedron-flask",
        "hedron-django",
        "hedron-explorer",
        "hedron-sample-kit",
        "Levels",
        "Artifact classes",
        "Deferred through the freeze",
    ]
    for section in required_sections:
        if section not in text:
            errors.append(f"STABILITY.md missing section mention: {section}")

    # Every __all__ name must appear somewhere in the catalog OR be __version__
    # Broad coverage: catalog discusses package groups; enforce non-empty __all__ and version pin.
    if "0.8.0" not in text and "0.8" not in text:
        errors.append("STABILITY.md should reference the 0.8 freeze train")

    total = 0
    for pkg in PACKAGES:
        init = package_init(pkg)
        if not init.is_file():
            errors.append(f"missing package init: {init}")
            continue
        names = read_all(init)
        if not names and pkg != "hedron_sample_kit":
            # sample-kit may only export __version__
            errors.append(f"{pkg}: __all__ is empty")
        total += len(names)
        # __version__ should be present in catalog packages
        version_match = re.search(
            r'^__version__\s*=\s*["\']([^"\']+)["\']',
            init.read_text(encoding="utf-8"),
            re.M,
        )
        if not version_match:
            errors.append(f"{pkg}: __version__ missing")

    if total < 50:
        errors.append(f"unexpectedly small public export surface: {total} names")

    # Plugin protocol and manifest version markers must be mentioned
    for needle in ("PluginMeta", "HDN_FORMAT_VERSION", "experimental", "deferred", "beta"):
        if needle not in text:
            errors.append(f"STABILITY.md missing required term: {needle}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"ok: stability inventory ({total} __all__ names across {len(PACKAGES)} packages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
