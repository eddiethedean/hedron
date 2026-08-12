#!/usr/bin/env python3
"""NOTEBOOK-031: localhost-only notebook preview tooling-grade evidence."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_031 import (  # noqa: E402
    fail_errors,
    require_files,
    require_inventory_supported,
    run_pytest,
)


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "packages" / "hedron-notebook" / "src" / "hedron_notebook" / "preview.py",
            ROOT / "docs" / "packages" / "hedron-notebook.md",
            ROOT / "tests" / "unit" / "test_phase17_notebook.py",
            ROOT / "tests" / "unit" / "test_notebook_031.py",
        ],
        errors,
    )
    require_inventory_supported(
        "hedron-notebook",
        (
            "localhost_only_preview",
            "iframe_isolation",
            "lifecycle_cleanup",
            "jupyter_compatibility_matrix",
        ),
        errors,
    )
    if fail_errors(errors, "NOTEBOOK-031"):
        return 1
    return run_pytest(
        [
            "tests/unit/test_phase17_notebook.py",
            "tests/unit/test_notebook_031.py",
        ],
        "NOTEBOOK-031",
    )


if __name__ == "__main__":
    raise SystemExit(main())
