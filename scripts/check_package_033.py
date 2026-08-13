#!/usr/bin/env python3
"""PACKAGE-033: hedron-posit distribution / extra / dependency graph (refine stub)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_033 import (  # noqa: E402
    fail_errors,
    require_files,
    require_inventory_keys,
    require_inventory_packages,
)


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "docs" / "acceptance" / "production-grade-inventory-033.toml",
            ROOT / "docs" / "acceptance" / "RELEASE_0_33.md",
        ],
        errors,
    )
    require_inventory_packages(("hedron-posit", "hedron-workbench"), errors)
    require_inventory_keys(
        "hedron-posit",
        supported=(
            "hedron_posit_facade",
            "posit_config",
            "native_connect",
            "workbench_delegation",
            "one_way_dependency_graph",
        ),
        experimental=("off_host_connect",),
        excluded=(
            "connect_publishing",
            "fastapi_posit_facade",
            "second_path_normalizer",
        ),
        errors=errors,
    )
    posit_pkg = ROOT / "packages" / "hedron-posit" / "pyproject.toml"
    if posit_pkg.is_file():
        text = posit_pkg.read_text(encoding="utf-8")
        if "hedron-workbench" in text and "dependencies" in text:
            # Soft check: dependency stanza must not list hedron-workbench.
            in_deps = False
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith("dependencies"):
                    in_deps = True
                    continue
                if in_deps and stripped.startswith("["):
                    in_deps = False
                if in_deps and "hedron-workbench" in stripped:
                    errors.append("hedron-posit must not depend on hedron-workbench")
                    break
    else:
        print("PACKAGE-033: packages/hedron-posit not present yet (packet refine)", file=sys.stderr)
    if fail_errors(errors, "PACKAGE-033"):
        return 1
    print("ok: PACKAGE-033")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
