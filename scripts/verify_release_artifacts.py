#!/usr/bin/env python3
"""Verify release-built artifacts against the approved reproducible candidate hashes."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/acceptance/compatibility-report-100/local-build-evidence.json"
DIST = ROOT / "dist"
EVIDENCE_ONLY_PATHS = {
    "docs/acceptance/compatibility-report-100/README.md",
    "docs/acceptance/compatibility-report-100/edron-build-evidence.json",
    "docs/acceptance/compatibility-report-100/local-bridge.json",
    "docs/acceptance/compatibility-report-100/local-build-evidence.json",
    "docs/acceptance/compatibility-report-100/verification-100.json",
}


def evidence_source_errors(source_commit: object) -> list[str]:
    """Return errors when an approved ledger no longer describes this checkout."""
    if not isinstance(source_commit, str) or len(source_commit) != 40:
        return ["approved release evidence source_commit must be a full commit hash"]
    try:
        changed = subprocess.check_output(
            ["git", "diff", "--name-only", f"{source_commit}..HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.STDOUT,
        ).splitlines()
        working_tree_changed = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD", "--"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.STDOUT,
        ).splitlines()
        untracked = subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.STDOUT,
        ).splitlines()
    except (OSError, subprocess.CalledProcessError):
        return ["approved release evidence source_commit is unavailable in this checkout"]
    unexpected = sorted(
        (set(changed) | set(working_tree_changed) | set(untracked)) - EVIDENCE_ONLY_PATHS
    )
    if unexpected:
        return [
            "approved release evidence is stale; source_commit predates non-evidence changes: "
            + ", ".join(unexpected[:5])
        ]
    return []


def main() -> int:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    expected = {
        str(item["name"]): str(item["sha256"])
        for item in evidence.get("artifacts", [])
        if isinstance(item, dict) and item.get("name") and item.get("sha256")
    }
    errors: list[str] = []
    errors.extend(evidence_source_errors(evidence.get("source_commit")))
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
