#!/usr/bin/env python3
"""COMPAT-029: isolation, upgrade goldens, Flask/Django untouched."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_029 import require_files, run_pytest  # noqa: E402


def _imports_workbench(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) and any(
            alias.name == "hedron_workbench" or alias.name.startswith("hedron_workbench.")
            for alias in node.names
        ):
            return True
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("hedron_workbench"):
            return True
    return False


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "tests" / "unit" / "test_workbench_isolation.py",
            ROOT / "tests" / "upgrade" / "test_0_28_2_to_0_29_workbench.py",
            ROOT / "docs" / "acceptance" / "upgrade-fixtures-029.md",
        ],
        errors,
    )
    forbidden = [
        ROOT / "packages" / "hedron" / "src" / "hedron" / "__init__.py",
        ROOT / "packages" / "hedron-core" / "src" / "hedron_core" / "__init__.py",
        ROOT / "packages" / "hedron-flask" / "src" / "hedron_flask" / "__init__.py",
        ROOT / "packages" / "hedron-django" / "src" / "hedron_django" / "__init__.py",
    ]
    for path in forbidden:
        if _imports_workbench(path):
            errors.append(f"{path.relative_to(ROOT)} must not import hedron_workbench")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if run_pytest(
        [
            "tests/unit/test_workbench_isolation.py",
            "tests/upgrade/test_0_28_2_to_0_29_workbench.py",
        ],
        "COMPAT-029",
    ):
        return 1
    print("ok: COMPAT-029")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
