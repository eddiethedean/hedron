"""FLEET-035 inventory coverage and disposition honesty."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-035.toml"
# Living whole-fleet coverage after Alpha hedron-elements (0.36); do not reopen FLEET-035.
LIVING_INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-036.toml"
VALID = {"production_grade", "incubator", "fixture", "eol"}


def test_inventory_covers_workspace_packages() -> None:
    data = tomllib.loads(LIVING_INVENTORY.read_text(encoding="utf-8"))
    packages = set(data["packages"])
    for pyproject in (ROOT / "packages").glob("*/pyproject.toml"):
        name = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]["name"]
        assert name in packages, name
    assert "hedron-runtime-node" in packages
    assert "hedron-runtime-java" in packages
    assert "hedron-elements" in packages


def test_every_row_has_owner_disposition_and_evidence() -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    for name in data["packages"]:
        row = data[name]
        assert row["owner"]
        assert row["disposition"] in VALID
        assert row["maturity"]
        assert row["channel"]
        assert row["pin"]
        assert row["evidence"]


def test_present_034_fold_in_recorded() -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    assert data["present_034_status"] == "deferred_to_fleet_docs_audit"
    assert set(data["present_034_gates"]) == {"FLEET-035", "DOCS-035"}
    core = data["hedron-core"]
    assert "default_presentation_gallery_refresh" in core["experimental"]


def test_no_unowned_alpha_rows() -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    for name in data["packages"]:
        row = data[name]
        if str(row.get("maturity", "")).lower() == "alpha":
            assert row["disposition"] in VALID
            assert row["owner"]
