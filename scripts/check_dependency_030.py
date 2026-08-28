#!/usr/bin/env python3
"""DEPENDENCY-030: one-way fastapi-workbench / hedron-workbench dependency boundary."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_030 import (  # noqa: E402
    FWB_PKG,
    HED_WB_PKG,
    require_files,
    run_pytest,
    workbench_pytest_paths,
)


def _imports_hedron(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) and any(
            alias.name == "hedron" or alias.name.startswith("hedron.") for alias in node.names
        ):
            return True
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "hedron" or module.startswith("hedron."):
                return True
            if module.startswith("hedron_"):
                return True
    return False


def main() -> int:
    errors: list[str] = []
    fwb_src = FWB_PKG / "src" / "fastapi_workbench"
    require_files(
        [
            FWB_PKG / "pyproject.toml",
            HED_WB_PKG / "pyproject.toml",
            ROOT / "docs" / "acceptance" / "production-grade-inventory-030.toml",
        ],
        errors,
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    for path in sorted(fwb_src.rglob("*.py")):
        if _imports_hedron(path):
            errors.append(f"{path.relative_to(ROOT)} must not import Hedron")

    hed_project = tomllib.loads((HED_WB_PKG / "pyproject.toml").read_text(encoding="utf-8")).get(
        "project", {}
    )
    deps = [str(dep) for dep in (hed_project.get("dependencies") or [])]
    if not any(dep.startswith("fastapi-workbench>=") for dep in deps):
        errors.append(
            "hedron-workbench pyproject.toml must depend on fastapi-workbench>=1.0.0,<2.0"
        )

    inventory = tomllib.loads(
        (ROOT / "docs" / "acceptance" / "production-grade-inventory-030.toml").read_text(
            encoding="utf-8"
        )
    )
    guards = inventory.get("install_guards") or {}
    if guards.get("fastapi_workbench_has_no_hedron_import") is not True:
        errors.append("install_guards.fastapi_workbench_has_no_hedron_import must be true")
    if guards.get("hedron_workbench_declares_fastapi_workbench") is not True:
        errors.append("install_guards.hedron_workbench_declares_fastapi_workbench must be true")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    if run_pytest(workbench_pytest_paths(), "DEPENDENCY-030"):
        return 1
    print("ok: DEPENDENCY-030")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
