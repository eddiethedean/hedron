#!/usr/bin/env python3
"""Verify phase 0.23 packaging / packet evidence for stable-tier expansion.

Does **not** publish or tag.

* Pre-cut / packet refine (``--allow-planned``): validate
  ``release-gate-0.23.toml`` shape leniently while package metadata stays on the
  living train (currently ``0.22.0``), plus focused facade/tier checkers.
* At ``v0.23.0`` cut (omit ``--allow-planned``): require Beta packages at
  ``0.23.0`` and every evidence row ``Verified``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "acceptance" / "release-gate-0.23.toml"
# Living published train while 0.23 gates remain Planned.
LIVING_TRAIN = "0.22.0"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-planned",
        action="store_true",
        help="Allow Planned rows (pre-cut / packet refine). Omit at v0.23.0 cut.",
    )
    args = parser.parse_args(argv)

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
            "0.23.0",
        ]

    commands = [
        gate_cmd,
        [sys.executable, str(ROOT / "scripts" / "check_stable_tier_023.py")],
        [sys.executable, str(ROOT / "scripts" / "check_stable_facade.py")],
        [sys.executable, str(ROOT / "scripts" / "check_stability_inventory.py")],
    ]
    for command in commands:
        print("+", *command)
        subprocess.check_call(command, cwd=ROOT)
    print("ok: PKG-023 packaging / packet evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
