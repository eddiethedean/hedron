#!/usr/bin/env python3
"""SUPPLY-035: fleet license/SBOM/offline notes + security review packet."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_035 import SUPPLY_DIR, fail_errors, require_files, run_pytest  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            SUPPLY_DIR / "LICENSE_INVENTORY.md",
            SUPPLY_DIR / "SBOM_NOTES.md",
            SUPPLY_DIR / "OFFLINE_INSTALL.md",
            SUPPLY_DIR / "ROLLBACK.md",
            ROOT / "docs" / "acceptance" / "security-review-035" / "BRIEF.md",
            ROOT / "docs" / "acceptance" / "security-review-035" / "REDACTED_REPORT.md",
            ROOT / "docs" / "acceptance" / "security-review-035" / "DISPOSITION.toml",
            ROOT / "scripts" / "build_evidence_bundle.py",
            ROOT / "scripts" / "dep_audit.py",
        ],
        errors,
    )
    for name, needles in (
        ("LICENSE_INVENTORY.md", ("MIT", "hedron", "Supported", "Experimental")),
        ("SBOM_NOTES.md", ("CycloneDX", "build_evidence_bundle", "retention")),
        ("OFFLINE_INSTALL.md", ("--no-index", "wheelhouse", "0.35")),
        ("ROLLBACK.md", ("rollback", "previous", "pin")),
    ):
        text = (SUPPLY_DIR / name).read_text(encoding="utf-8") if (SUPPLY_DIR / name).is_file() else ""
        for needle in needles:
            if needle not in text:
                errors.append(f"{name} missing {needle!r}")
    disposition = ROOT / "docs" / "acceptance" / "security-review-035" / "DISPOSITION.toml"
    if disposition.is_file():
        data = tomllib.loads(disposition.read_text(encoding="utf-8"))
        if data.get("critical_high_open") is not False:
            errors.append("DISPOSITION.toml critical_high_open must be false")
    if fail_errors(errors, "SUPPLY-035"):
        return 1
    if run_pytest(["tests/ops/test_supply_035.py"], "SUPPLY-035"):
        return 1
    print("ok: SUPPLY-035")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
