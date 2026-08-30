#!/usr/bin/env python3
"""Verify Edron-lane artifacts against the approved reproducible hash ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

try:
    from .verify_release_artifacts import evidence_source_errors
except ImportError:  # pragma: no cover - direct script execution
    from verify_release_artifacts import evidence_source_errors

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/acceptance/compatibility-report-100/edron-build-evidence.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args()

    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    expected = {
        str(item["name"]): str(item["sha256"])
        for item in evidence.get("artifacts", [])
        if isinstance(item, dict) and item.get("name") and item.get("sha256")
    }
    required_prefixes = ("edron-", "edron_sim-")
    errors: list[str] = []
    errors.extend(evidence_source_errors(evidence.get("source_commit")))
    if len(expected) != 4 or any(
        sum(name.startswith(prefix) for name in expected) != 2 for prefix in required_prefixes
    ):
        errors.append("approved Edron lane must contain wheel/sdist hashes for edron and edron-sim")

    dist_dir = args.dist_dir.resolve()
    actual_names = {
        path.name
        for path in dist_dir.iterdir()
        if path.is_file()
        and path.name != ".gitignore"
        and (path.suffix == ".whl" or path.name.endswith(".tar.gz"))
    }
    if actual_names != set(expected):
        errors.append(
            "Edron release artifact inventory differs from approval: "
            f"expected={sorted(expected)!r}, actual={sorted(actual_names)!r}"
        )

    for name, digest in sorted(expected.items()):
        path = dist_dir / name
        if not path.is_file():
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            errors.append(f"{name}: approved sha256={digest}, release build sha256={actual}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"ok: Edron release build matches {len(expected)} approved artifact hashes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
