#!/usr/bin/env python3
"""PLUGIN-031: external sample-kit consumer evidence."""

from __future__ import annotations

import subprocess
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
            ROOT / "packages" / "hedron-sample-kit" / "src" / "hedron_sample_kit" / "plugin.py",
            ROOT / "examples" / "sample-kit-consumer" / "verify_consumer.py",
            ROOT / "examples" / "sample-kit-consumer" / "README.md",
            ROOT / "tests" / "unit" / "test_plugin_031.py",
        ],
        errors,
    )
    require_inventory_supported(
        "hedron-sample-kit",
        (
            "external_plugin_exemplar",
            "entry_point_discovery",
            "assets_diagnostics",
            "explorer_panels",
            "disable_uninstall",
        ),
        errors,
    )
    if fail_errors(errors, "PLUGIN-031"):
        return 1
    code = run_pytest(
        [
            "tests/unit/test_phase04_platform.py::test_sample_kit_plugin_module",
            "tests/unit/test_plugin_031.py",
        ],
        "PLUGIN-031",
    )
    if code:
        return code
    cmd = [
        sys.executable,
        str(ROOT / "examples" / "sample-kit-consumer" / "verify_consumer.py"),
    ]
    print("+", *cmd)
    try:
        subprocess.check_call(cmd, cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        print(f"PLUGIN-031 consumer failed ({exc.returncode})", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
