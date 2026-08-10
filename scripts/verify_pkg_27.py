#!/usr/bin/env python3
"""Verify phase 0.27 packaging / packet evidence for satellite graduation.

Does **not** publish or tag.

* Default / ``--allow-planned``: validate the 0.27 evidence manifest shape while
  package metadata remains on the living **0.26.x** train (packet refine).
* Omit ``--allow-planned`` only at ``v0.27.0`` cut, after package versions bump
  and every evidence row is ``Verified``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "acceptance" / "release-gate-0.27.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-027.toml"
# Living published tip while the 0.27 packet is open (packages not yet 0.27.0).
LIVING_TRAIN = "0.27.0"
RELEASE_CANDIDATE = "0.27.0"
EXPECTED_PACKAGES = (
    "hedron-data",
    "hedron-flask",
    "hedron-django",
    "hedron-jinja",
    "hedron-extras",
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
    if str(data.get("baseline", "")).strip() != "v0.26.0":
        raise SystemExit(f"{INVENTORY}: baseline must be v0.26.0")
    print("ok: production-grade-inventory-027.toml")


def _check_contract() -> None:
    cmd = [sys.executable, str(ROOT / "scripts" / "check_contract_027.py")]
    print("+", *cmd)
    subprocess.check_call(cmd, cwd=ROOT)


def _check_security_review_packet() -> None:
    review = ROOT / "docs" / "acceptance" / "security-review-027"
    for name in ("BRIEF.md", "REDACTED_REPORT.md", "DISPOSITION.toml"):
        path = review / name
        if not path.is_file():
            raise SystemExit(f"missing security review artifact: {path}")
    disposition = tomllib.loads((review / "DISPOSITION.toml").read_text(encoding="utf-8"))
    if disposition.get("critical_high_open") is not False:
        raise SystemExit("security-review-027 DISPOSITION critical_high_open must be false")
    print("ok: security-review-027 packet")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-planned",
        action="store_true",
        help=(
            f"Allow Planned rows (pre-cut / packet refine). "
            f"Omit at v{RELEASE_CANDIDATE} cut."
        ),
    )
    args = parser.parse_args(argv)

    _check_inventory()
    _check_contract()
    _check_security_review_packet()

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
    print("ok: PKG-027 packaging / packet evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
