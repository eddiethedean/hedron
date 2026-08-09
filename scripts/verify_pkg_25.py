#!/usr/bin/env python3
"""Verify phase 0.25 packaging / packet evidence for archetype and landmines.

Does **not** publish or tag.

* Default (omit ``--allow-planned``): require every evidence row ``Verified``, then
  execute Verified SSOT ``check_*.py`` commands from the manifest (cut path).
* ``--allow-planned`` remains for lenient gate shape checks against living
  train metadata (``0.24.0``).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "acceptance" / "release-gate-0.25.toml"
# Living published train (also used with --allow-planned post-cut until 0.25 publishes).
LIVING_TRAIN = "0.24.0"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-planned",
        action="store_true",
        help="Allow Planned rows (pre-cut / packet refine). Omit at v0.25.0 cut.",
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
            "0.25.0",
            "--execute-verified",
        ]

    print("+", *gate_cmd)
    subprocess.check_call(gate_cmd, cwd=ROOT)
    print("ok: PKG-025 packaging / packet evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
