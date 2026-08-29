#!/usr/bin/env python3
"""Ensure every hedron root ``__all__`` name has a symbol tier classification."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "packages" / "hedron" / "src" / "hedron" / "__init__.py"
TIERS = ROOT / "docs" / "api" / "export_tiers.toml"
ALLOWED_TIERS = frozenset({"stable", "beta", "experimental", "internal"})


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


def experimental_shims(text: str) -> set[str]:
    match = re.search(
        r"_EXPERIMENTAL_EXPORTS\s*=\s*frozenset\(\s*\{([^}]+)\}",
        text,
        re.S,
    )
    if not match:
        return set()
    return set(re.findall(r'"([A-Za-z_][A-Za-z0-9_]*)"', match.group(1)))


def main() -> int:
    errors: list[str] = []
    if not TIERS.is_file():
        print(f"missing {TIERS.relative_to(ROOT)}", file=sys.stderr)
        return 1

    data = tomllib.loads(TIERS.read_text(encoding="utf-8"))
    hedron_table = data.get("hedron")
    if not isinstance(hedron_table, dict):
        print("export_tiers.toml missing [hedron] table", file=sys.stderr)
        return 1

    classified = {k: v for k, v in hedron_table.items() if isinstance(v, str)}
    nested = hedron_table.get("experimental_shims")
    shim_map = (
        {k: v for k, v in nested.items() if isinstance(v, str)} if isinstance(nested, dict) else {}
    )

    names = read_all(INIT)
    if not names:
        errors.append("hedron.__all__ is empty or unreadable")

    for name in names:
        tier = classified.get(name)
        if tier is None:
            errors.append(f"unclassified hedron export: {name}")
        elif tier not in ALLOWED_TIERS:
            errors.append(f"invalid tier for {name}: {tier!r}")

    for name in sorted(set(classified) - set(names)):
        errors.append(f"export_tiers.toml lists unknown hedron.__all__ name: {name}")

    text = INIT.read_text(encoding="utf-8")
    expected_shims = experimental_shims(text)
    for name in sorted(expected_shims):
        if shim_map.get(name) != "experimental":
            errors.append(f"experimental shim {name!r} must be classified experimental")
    for name in sorted(set(shim_map) - expected_shims):
        errors.append(f"stale experimental shim classification: {name}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"ok: symbol tiers ({len(names)} __all__, {len(expected_shims)} experimental shims)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
