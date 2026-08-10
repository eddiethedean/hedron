#!/usr/bin/env python3
"""CORE-026: upgrade fixtures from v0.25.2 + facade golden suite."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "acceptance" / "upgrade-fixtures-026.md"
TEST = ROOT / "tests" / "upgrade" / "test_0_25_2_to_0_26_facade.py"
GOLDENS = ROOT / "tests" / "upgrade" / "goldens_0_25_2"


def main() -> int:
    errors: list[str] = []
    if not PLAN.is_file():
        errors.append(f"missing {PLAN.relative_to(ROOT)}")
    else:
        text = PLAN.read_text(encoding="utf-8")
        for needle in ("v0.25.2", "identities", "Diagnostics", "manifests", "HTMX"):
            if needle not in text and needle.lower() not in text.lower():
                errors.append(f"upgrade-fixtures-026.md missing {needle!r}")
    if not TEST.is_file():
        errors.append(f"missing {TEST.relative_to(ROOT)}")
    if not GOLDENS.is_dir():
        errors.append(f"missing {GOLDENS.relative_to(ROOT)}")
    else:
        required = (
            "identities.json",
            "diagnostics.json",
            "manifest_keys.json",
            "htmx_interaction.json",
        )
        for name in required:
            if not (GOLDENS / name).is_file():
                errors.append(f"missing golden {name}")

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
        print(f"CORE-026 pytest failed ({exc.returncode})", file=sys.stderr)
        return 1
    print("ok: CORE-026 upgrade fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
