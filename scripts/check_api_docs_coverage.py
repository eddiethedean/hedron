#!/usr/bin/env python3
"""Fail when a public ``hedron`` export disappears from the API coverage map."""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "packages/hedron/src/hedron/__init__.py"
COVERAGE = ROOT / "docs/api/COVERAGE.md"


def public_exports(source: str) -> set[str]:
    tree = ast.parse(source)
    assignments = [
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets)
    ]
    if not assignments:
        raise ValueError("hedron.__all__ assignment not found")
    value = ast.literal_eval(assignments[-1].value)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError("hedron.__all__ must be a literal list of strings")
    return set(value)


def documented_symbols(markdown: str) -> set[str]:
    symbols: set[str] = set()
    for span in re.findall(r"`([^`\n]+)`", markdown):
        for token in re.split(r"\s*,\s*", span):
            token = token.strip()
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token):
                symbols.add(token)
    return symbols


def main() -> int:
    exports = public_exports(INIT.read_text(encoding="utf-8"))
    documented = documented_symbols(COVERAGE.read_text(encoding="utf-8"))
    missing = sorted(exports - documented)
    if missing:
        raise SystemExit(
            "docs/api/COVERAGE.md is missing public exports:\n  " + "\n  ".join(missing)
        )
    print(f"ok: all {len(exports)} hedron.__all__ exports appear in the API coverage map")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
