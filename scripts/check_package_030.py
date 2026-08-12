#!/usr/bin/env python3
"""PACKAGE-030: monorepo fastapi-workbench 1.0.0 package ownership."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_030 import FWB_PKG, require_files, run_pytest, workbench_pytest_paths  # noqa: E402

PROVENANCE = ROOT / "docs" / "acceptance" / "fastapi-workbench-provenance-030.toml"


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            FWB_PKG / "pyproject.toml",
            FWB_PKG / "README.md",
            FWB_PKG / "CHANGELOG.md",
            FWB_PKG / "LICENSE",
            FWB_PKG / "src" / "fastapi_workbench" / "__init__.py",
            FWB_PKG / "src" / "fastapi_workbench" / "resolve.py",
            FWB_PKG / "src" / "fastapi_workbench" / "middleware.py",
            FWB_PKG / "src" / "fastapi_workbench" / "runner.py",
            FWB_PKG / "src" / "fastapi_workbench" / "cli.py",
            PROVENANCE,
        ],
        errors,
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    pyproject = tomllib.loads((FWB_PKG / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject.get("project") or {}
    if project.get("name") != "fastapi-workbench":
        print("fastapi-workbench pyproject name must be fastapi-workbench", file=sys.stderr)
        return 1
    if project.get("version") != "1.0.0":
        print("fastapi-workbench version must be 1.0.0", file=sys.stderr)
        return 1
    deps = project.get("dependencies") or []
    if any(str(dep).startswith("hedron") for dep in deps):
        print("fastapi-workbench must not declare Hedron dependencies", file=sys.stderr)
        return 1

    prov = tomllib.loads(PROVENANCE.read_text(encoding="utf-8"))
    if prov.get("version") != "1.0.0" or prov.get("ownership") != "monorepo":
        print("provenance must record monorepo-owned 1.0.0", file=sys.stderr)
        return 1

    if run_pytest(workbench_pytest_paths(), "PACKAGE-030"):
        return 1
    print("ok: PACKAGE-030")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
