#!/usr/bin/env python3
"""Verify release-built artifacts against the approved reproducible candidate hashes."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/acceptance/compatibility-report-100/local-build-evidence.json"
DIST = ROOT / "dist"


def main() -> int:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    expected = {
        str(item["name"]): str(item["sha256"])
        for item in evidence.get("artifacts", [])
        if isinstance(item, dict) and item.get("name") and item.get("sha256")
    }
    errors: list[str] = []
    for name, digest in sorted(expected.items()):
        path = DIST / name
        if not path.is_file():
            errors.append(f"missing approved release artifact: {name}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            errors.append(f"{name}: approved sha256={digest}, release build sha256={actual}")
    if len(expected) != 26:
        errors.append(f"approved coordinated artifact count must be 26, found {len(expected)}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"ok: release build matches {len(expected)} approved artifact hashes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
