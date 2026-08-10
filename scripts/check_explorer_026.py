#!/usr/bin/env python3
"""EXPLORER-026: secured-mode authz / audit / CSP / payload / production refusal."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "tests" / "integration" / "test_explorer_026.py"
DOCS = (
    ROOT / "docs" / "api" / "EXPLORER.md",
    ROOT / "docs" / "packages" / "hedron-explorer.md",
)


def main() -> int:
    errors: list[str] = []
    if not TEST.is_file():
        errors.append(f"missing {TEST.relative_to(ROOT)}")
    for path in DOCS:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for needle in ("secured", "auth", "production"):
            if needle.lower() not in text.lower():
                errors.append(f"{path.relative_to(ROOT)} missing {needle!r}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(TEST.relative_to(ROOT)),
        "-q",
        "--tb=short",
    ]
    print("+", *cmd)
    try:
        subprocess.check_call(cmd, cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        print(f"EXPLORER-026 pytest failed ({exc.returncode})", file=sys.stderr)
        return 1
    print("ok: EXPLORER-026 secured-mode evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
