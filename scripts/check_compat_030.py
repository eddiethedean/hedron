#!/usr/bin/env python3
"""COMPAT-030: isolation, upgrade goldens, Flask/Django untouched."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_030 import require_files, run_pytest, workbench_pytest_paths  # noqa: E402


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
    upgrade_tests = [
        ROOT / "tests" / "upgrade" / "test_0_29_0_to_0_30_workbench.py",
        ROOT / "tests" / "upgrade" / "test_fwb_034_to_1_0.py",
    ]
    require_files(
        [
            ROOT / "tests" / "unit" / "test_workbench_isolation.py",
            ROOT / "docs" / "acceptance" / "upgrade-fixtures-030.md",
            *upgrade_tests,
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
        if path.is_file() and _imports_workbench(path):
            errors.append(f"{path.relative_to(ROOT)} must not import hedron_workbench")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    paths = [
        "tests/unit/test_workbench_isolation.py",
        "tests/upgrade/test_0_29_0_to_0_30_workbench.py",
        "tests/upgrade/test_fwb_034_to_1_0.py",
        *workbench_pytest_paths(),
    ]
    if run_pytest(list(dict.fromkeys(paths)), "COMPAT-030"):
        return 1
    print("ok: COMPAT-030")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
