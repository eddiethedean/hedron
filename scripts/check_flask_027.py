#!/usr/bin/env python3
"""FLASK-027: host-only Flask adapter graduation evidence."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_027 import require_files, require_inventory_supported, run_pytest, run_script  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "examples" / "flask-reference" / "app.py",
            ROOT / "docs" / "getting-started" / "flask.md",
        ],
        errors,
    )
    require_inventory_supported(
        "hedron-flask",
        (
            "flask_pages",
            "flask_fragments",
            "flask_actions",
            "host_owned_sessions_csrf_auth",
            "polling_jobs",
            "scaffolds",
        ),
        errors,
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if run_script("scripts/smoke_flask_027.py", "FLASK-027 smoke"):
        return 1
    if run_pytest(
        [
            "tests/adapters/flask/test_flask_adapter.py",
            "tests/adapters/flask/test_flask_hardening.py",
            "tests/upgrade/test_0_26_0_to_0_27_satellites.py::test_adapter_interaction_polling_only",
        ],
        "FLASK-027",
    ):
        return 1
    print("ok: FLASK-027")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
