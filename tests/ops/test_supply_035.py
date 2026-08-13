"""SUPPLY-035 fleet packet shape."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUPPLY = ROOT / "docs" / "acceptance" / "fleet-supply-035"
REVIEW = ROOT / "docs" / "acceptance" / "security-review-035"


def test_supply_packet_files_exist() -> None:
    for name in ("LICENSE_INVENTORY.md", "SBOM_NOTES.md", "OFFLINE_INSTALL.md", "ROLLBACK.md"):
        assert (SUPPLY / name).is_file()


def test_security_disposition_closes_critical_high() -> None:
    data = tomllib.loads((REVIEW / "DISPOSITION.toml").read_text(encoding="utf-8"))
    assert data["critical_high_open"] is False


def test_evidence_scripts_exist() -> None:
    assert (ROOT / "scripts" / "build_evidence_bundle.py").is_file()
    assert (ROOT / "scripts" / "dep_audit.py").is_file()
