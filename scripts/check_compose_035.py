#!/usr/bin/env python3
"""COMPOSE-035: reference-app isolation and Supported combination evidence."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_035 import RELEASE_PACKET, fail_errors, require_files, run_pytest  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            RELEASE_PACKET,
            ROOT / "examples" / "reference-app" / "app.py",
            ROOT / "examples" / "reference-app" / "docker-compose.yml",
            ROOT / "docs" / "api" / "PRODUCTION_ARCHETYPE.md",
        ],
        errors,
    )
    release = RELEASE_PACKET.read_text(encoding="utf-8") if RELEASE_PACKET.is_file() else ""
    if "test_compose_035" not in release and "COMPOSE-035" not in release:
        errors.append("RELEASE_0_35 must reference COMPOSE-035 evidence")
    if fail_errors(errors, "COMPOSE-035"):
        return 1
    if run_pytest(["tests/ops/test_compose_035.py"], "COMPOSE-035"):
        return 1
    print("ok: COMPOSE-035")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
