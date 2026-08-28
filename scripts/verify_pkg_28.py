#!/usr/bin/env python3
"""Verify phase 0.28 packaging / packet evidence for charts and native graduation.

Does **not** publish or tag.

* ``--allow-planned``: validate the 0.28 evidence manifest shape while rows may
  still be Planned (packet refine).
* Omit ``--allow-planned`` at ``v0.28.2`` cut once every evidence row is
  ``Verified`` and package metadata matches the living **0.28.x** train.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "acceptance" / "release-gate-0.28.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-028.toml"
# Living published tip after the 0.28 cut.
LIVING_TRAIN = "0.28.2"
RELEASE_CANDIDATE = "0.28.2"
EXPECTED_PACKAGES = (
    "hedron-charts",
    "hedron-native",
)


def _check_inventory() -> None:
    if not INVENTORY.is_file():
        raise SystemExit(f"missing inventory: {INVENTORY}")
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    packages = data.get("packages")
    if not isinstance(packages, list):
        raise SystemExit(f"{INVENTORY}: packages list required")
    missing = [name for name in EXPECTED_PACKAGES if name not in packages]
    if missing:
        raise SystemExit(f"{INVENTORY}: missing packages {missing}")
    if str(data.get("baseline", "")).strip() != "v0.27.0":
        raise SystemExit(f"{INVENTORY}: baseline must be v0.27.0")
    print("ok: production-grade-inventory-028.toml")


def _check_contract() -> None:
    cmd = [sys.executable, str(ROOT / "scripts" / "check_contract_028.py")]
    print("+", *cmd)
    subprocess.check_call(cmd, cwd=ROOT)


def _check_security_review_packet(*, allow_planned: bool) -> None:
    review = ROOT / "docs" / "acceptance" / "security-review-028"
    brief = review / "BRIEF.md"
    if not brief.is_file():
        raise SystemExit(f"missing security review artifact: {brief}")
    if allow_planned:
        print("ok: security-review-028 BRIEF (Planned packet)")
        return
    for name in ("REDACTED_REPORT.md", "DISPOSITION.toml"):
        path = review / name
        if not path.is_file():
            raise SystemExit(f"missing security review artifact: {path}")
    disposition = tomllib.loads((review / "DISPOSITION.toml").read_text(encoding="utf-8"))
    if disposition.get("critical_high_open") is not False:
        raise SystemExit("security-review-028 DISPOSITION critical_high_open must be false")
    print("ok: security-review-028 packet")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-planned",
        action="store_true",
        help=(f"Allow Planned rows (pre-cut / packet refine). Omit at v{RELEASE_CANDIDATE} cut."),
    )
    args = parser.parse_args(argv)

    _check_inventory()
    _check_contract()
    _check_security_review_packet(allow_planned=args.allow_planned)

    if args.allow_planned:
        gate_cmd = [
            sys.executable,
            str(ROOT / "scripts" / "check_release_gate.py"),
            LIVING_TRAIN,
            "--evidence-manifest",
            str(EVIDENCE),
            "--allow-planned",
        ]
    else:
        gate_cmd = [
            sys.executable,
            str(ROOT / "scripts" / "check_release_gate.py"),
            RELEASE_CANDIDATE,
            "--evidence-manifest",
            str(EVIDENCE),
            "--execute-verified",
        ]

    print("+", *gate_cmd)
    subprocess.check_call(gate_cmd, cwd=ROOT)
    print("ok: PKG-028 packaging / packet evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
