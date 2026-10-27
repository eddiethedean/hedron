#!/usr/bin/env python3
"""Verify the in-tree Python 3.11+ package baseline and phase packet."""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_python_311  # noqa: E402
import check_release_gate  # noqa: E402

EXPECTED_GATES = check_release_gate.PHASE_120_EVIDENCE_IDS


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-planned",
        action="store_true",
        help="Check in-tree implementation while matrix/artifact evidence is still being collected",
    )
    args = parser.parse_args()
    failures = check_python_311.check()

    release = tomllib.loads((ROOT / "docs" / "release.toml").read_text(encoding="utf-8"))
    if release.get("release", {}).get("development_version") != "1.2.0":
        failures.append("docs/release.toml must select development version 1.2.0")
    if release.get("edron", {}).get("development_version") != "1.2.0":
        failures.append("docs/release.toml must select Edron development version 1.2.0")
    failures.extend(check_release_gate.check_packages("1.2.0"))

    manifest_path = ROOT / "docs" / "acceptance" / "release-gate-1.2.toml"
    manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    rows = manifest.get("evidence")
    found = tuple(str(row.get("id", "")).strip() for row in rows or [] if isinstance(row, dict))
    if found != EXPECTED_GATES:
        failures.append(f"release-gate-1.2.toml gate order mismatch: {found!r}")
    if manifest.get("phase") != "1.2" or manifest.get("target") != "v1.2.0":
        failures.append("release-gate-1.2.toml must select phase 1.2 / target 1.2.0")
    if manifest.get("support_policy_amendment_accepted") is not True:
        failures.append("D-120 support policy amendment must be recorded as accepted")
    if manifest.get("stage_1_entry_satisfied") is not True:
        failures.append("phase 1.2 implementation entry must be recorded as satisfied")
    states = {str(row.get("state", "")) for row in rows or [] if isinstance(row, dict)}
    if not args.allow_planned and states.intersection({"Planned", "Implemented", "Blocked"}):
        failures.append(
            "release evidence is incomplete; pass --allow-planned only for implementation CI"
        )
    if not args.allow_planned:
        failures.extend(check_release_gate.check_evidence_manifest(manifest_path))
    else:
        failures.extend(check_release_gate.check_evidence_manifest_lenient(manifest_path))

    if failures:
        print("\n".join(f"error: {failure}" for failure in failures), file=sys.stderr)
        return 1
    phase = "implementation" if args.allow_planned else "release evidence"
    print(f"ok: phase 1.2 {phase} packet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
