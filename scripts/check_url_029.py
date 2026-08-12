#!/usr/bin/env python3
"""URL-029: Hedron mount/redirect/CSRF/cookie composition under Workbench."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_029 import require_files, run_pytest  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "packages" / "hedron-workbench" / "src" / "hedron_workbench" / "urls.py",
            ROOT / "packages" / "hedron-workbench" / "src" / "hedron_workbench" / "app.py",
            ROOT / "tests" / "integration" / "test_workbench_urls.py",
        ],
        errors,
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if run_pytest(["tests/integration/test_workbench_urls.py"], "URL-029"):
        return 1
    print("ok: URL-029")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
