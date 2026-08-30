#!/usr/bin/env python3
"""PARITY-027: portable FastAPI/Flask/Django Supported interaction parity."""

from __future__ import annotations

import sys
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_027 import require_files, run_pytest  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "tests" / "conformance" / "test_parity_027.py",
            ROOT / "docs" / "acceptance" / "security-review-027" / "BRIEF.md",
            ROOT / "docs" / "acceptance" / "security-review-027" / "REDACTED_REPORT.md",
            ROOT / "docs" / "acceptance" / "security-review-027" / "DISPOSITION.toml",
        ],
        errors,
    )
    disposition = ROOT / "docs" / "acceptance" / "security-review-027" / "DISPOSITION.toml"
    if disposition.is_file():
        data = tomllib.loads(disposition.read_text(encoding="utf-8"))
        if data.get("critical_high_open") is not False:
            errors.append("security-review-027 critical_high_open must be false")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    if run_pytest(
        [
            "tests/conformance/test_parity_027.py",
            "tests/conformance/test_portable_interaction.py",
            "tests/conformance/test_adapter_harness.py",
            "tests/unit/test_review_027_adversarial.py",
            "tests/upgrade/test_0_26_0_to_0_27_satellites.py::test_adapter_interaction_polling_only",
        ],
        "PARITY-027",
    ):
        return 1
    print("ok: PARITY-027")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
