#!/usr/bin/env python3
"""FASTAPI-030: plain FastAPI hands-off Workbench launcher."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_030 import FWB_PKG, require_files, run_pytest, workbench_pytest_paths  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            FWB_PKG / "src" / "fastapi_workbench" / "runner.py",
            FWB_PKG / "src" / "fastapi_workbench" / "cli.py",
            ROOT / "tests" / "integration" / "test_fastapi_mvp.py",
        ],
        errors,
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    paths = ["tests/integration/test_fastapi_mvp.py", *workbench_pytest_paths()]
    if run_pytest(list(dict.fromkeys(paths)), "FASTAPI-030"):
        return 1
    print("ok: FASTAPI-030")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
