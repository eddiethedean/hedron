#!/usr/bin/env python3
"""Verify phase 0.31 packaging / packet evidence for tooling + migrator.

Does **not** publish or tag.

* ``--allow-planned``: validate the 0.31 evidence manifest shape while rows may
  still be Planned and the living tip remains on ``0.30.x`` (packet refine).
* Omit ``--allow-planned`` at ``v0.31.0`` cut once every evidence row is
  ``Verified`` and package metadata matches the **0.31.x** train.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "acceptance" / "release-gate-0.31.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-031.toml"
# During refine, package metadata still tracks the published tip.
LIVING_TIP = "0.30.0"
RELEASE_CANDIDATE = "0.31.0"
EXPECTED_PACKAGES = (
    "hedron-conformance",
    "hedron-sample-kit",
    "hedron-sim",
    "hedron-notebook",
    "hedron-runtime-node",
    "hedron-runtime-java",
    "hedron",
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
    if str(data.get("baseline", "")).strip() != "v0.30.0":
        raise SystemExit(f"{INVENTORY}: baseline must be v0.30.0")
    print("ok: production-grade-inventory-031.toml")


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

    if args.allow_planned:
        # Tip honesty remains 0.30.x; only the 0.31 evidence shape is validated.
        gate_cmd = [
            sys.executable,
            str(ROOT / "scripts" / "check_release_gate.py"),
            LIVING_TIP,
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
    print(f"ok: verify_pkg_31 ({'allow-planned' if args.allow_planned else 'cut'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
