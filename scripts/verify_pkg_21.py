#!/usr/bin/env python3
"""Verify phase 0.21 packaging / packet evidence that can run without human AT sessions.

Does **not** require ``--require-sessions`` and does **not** publish or tag. Package
metadata and adopter docs may already claim the 0.21 train; human AT SR/PARTICIPANT
remain Planned until real sessions.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FOCUSED_TESTS = [
    "tests/unit/test_phase19_governance.py",
    "tests/integration/test_reference_crud.py",
    "tests/unit/test_human_at_packet.py",
    "tests/unit/test_theme_assets_build.py::test_data_editor_enhancement_hides_no_script_fallback",
    "tests/adapters/test_phase20_fragment_regions.py::test_flask_action_declared_fragment_regions_allow_hx_target",
    "tests/adapters/test_phase20_fragment_regions.py::test_flask_action_undeclared_hx_target_is_forbidden",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)

    commands = [
        [sys.executable, str(ROOT / "scripts" / "check_human_at_packet.py")],
        [sys.executable, "-m", "pytest", "-q", *FOCUSED_TESTS],
        [
            sys.executable,
            str(ROOT / "scripts" / "check_release_gate.py"),
            "0.21.0",
            "--allow-planned",
        ],
    ]
    for command in commands:
        print("+", *command)
        subprocess.check_call(command, cwd=ROOT)
    print("ok: PKG-021 local packaging / packet evidence (sessions still Planned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
