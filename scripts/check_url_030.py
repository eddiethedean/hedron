#!/usr/bin/env python3
"""URL-030: mount/redirect/cookie composition under Workbench."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_030 import (  # noqa: E402
    FWB_PKG,
    HED_WB_PKG,
    require_files,
    run_pytest,
    workbench_pytest_paths,
)


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            FWB_PKG / "src" / "fastapi_workbench" / "urls.py",
            HED_WB_PKG / "src" / "hedron_workbench" / "urls.py",
            ROOT / "tests" / "integration" / "test_workbench_urls.py",
        ],
        errors,
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    paths = ["tests/integration/test_workbench_urls.py", *workbench_pytest_paths()]
    if run_pytest(list(dict.fromkeys(paths)), "URL-030"):
        return 1
    print("ok: URL-030")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
