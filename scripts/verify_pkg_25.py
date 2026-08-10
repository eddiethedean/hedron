#!/usr/bin/env python3
"""Verify phase 0.25 packaging / packet evidence for archetype and landmines.

Does **not** publish or tag.

* Default (omit ``--allow-planned``): require every evidence row ``Verified``, then
  execute Verified SSOT ``check_*.py`` commands from the manifest (cut path).
* ``--allow-planned`` remains for lenient gate shape checks against living
  train metadata.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "acceptance" / "release-gate-0.25.toml"
# Prepared patch candidate. This does not imply that the tag or packages are published.
RELEASE_CANDIDATE = "0.25.1"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-planned",
        action="store_true",
        help=f"Allow Planned rows (pre-cut / packet refine). Omit at v{RELEASE_CANDIDATE} cut.",
    )
    args = parser.parse_args(argv)

    if args.allow_planned:
        gate_cmd = [
            sys.executable,
            str(ROOT / "scripts" / "check_release_gate.py"),
            RELEASE_CANDIDATE,
            "--evidence-manifest",
            str(EVIDENCE),
            "--allow-planned",
        ]
    else:
        gate_cmd = [
            sys.executable,
            str(ROOT / "scripts" / "check_release_gate.py"),
            RELEASE_CANDIDATE,
            "--execute-verified",
        ]

    print("+", *gate_cmd)
    subprocess.check_call(gate_cmd, cwd=ROOT)
    print("ok: PKG-025 packaging / packet evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
