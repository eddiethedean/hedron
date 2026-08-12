#!/usr/bin/env python3
"""CONF-031: conformance tooling-grade evidence."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_031 import (  # noqa: E402
    fail_errors,
    require_dirs,
    require_files,
    require_inventory_supported,
    run_pytest,
)

PKG = ROOT / "packages" / "hedron-conformance" / "src" / "hedron_conformance"


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            PKG / "compat.py",
            PKG / "author.py",
            PKG / "author_kit" / "README.md",
            PKG / "author_kit" / "runtime_template.md",
            PKG / "fixtures" / "portable_v1.json",
            ROOT / "docs" / "acceptance" / "upgrade-fixtures-031.md",
            ROOT / "tests" / "unit" / "test_conformance_031.py",
        ],
        errors,
    )
    require_dirs([PKG / "author_kit", PKG / "fixtures"], errors)
    require_inventory_supported(
        "hedron-conformance",
        (
            "versioned_schemas",
            "golden_fixtures",
            "runner_cli_api",
            "compatibility_policy",
            "third_party_runtime_author_kit",
        ),
        errors,
    )
    if fail_errors(errors, "CONF-031"):
        return 1
    return run_pytest(
        [
            "tests/unit/test_conformance_kit.py",
            "tests/unit/test_conformance_spec.py",
            "tests/unit/test_conformance_031.py",
        ],
        "CONF-031",
    )


if __name__ == "__main__":
    raise SystemExit(main())
