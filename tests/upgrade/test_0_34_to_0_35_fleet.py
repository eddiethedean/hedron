"""Upgrade fixtures for fleet closure 0.34 -> 0.35."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-035.toml"
RELEASE = ROOT / "docs" / "release.toml"


def test_inventory_baseline_is_v0_34() -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    assert data["baseline"] == "v0.34.0"


def test_release_toml_train_is_documented_for_cut() -> None:
    # Historical cut facts remain documented even after later tip bumps.
    data = tomllib.loads(RELEASE.read_text(encoding="utf-8"))["release"]
    if data["train"] == "0.45":
        assert data["previous_train"] == "0.44"
        assert data["previous_version"] == "0.44.0"
    elif data["train"] == "0.44":
        assert data["previous_train"] == "0.43"
        assert data["previous_version"] == "0.43.0"
    elif data["train"] == "0.43":
        assert data["previous_train"] == "0.42"
        assert data["previous_version"] == "0.42.0"
    elif data["train"] == "0.42":
        assert data["previous_train"] == "0.41"
        assert data["previous_version"] == "0.41.0"
    elif data["train"] == "0.41":
        assert data["previous_train"] == "0.40"
        assert data["previous_version"] == "0.40.0"
    elif data["train"] == "0.40":
        assert data["previous_train"] == "0.39"
        assert data["previous_version"] == "0.39.0"
    elif data["train"] == "0.39":
        assert data["previous_train"] == "0.38"
        assert data["previous_version"] == "0.38.0"
    elif data["train"] == "0.38":
        assert data["previous_train"] == "0.37"
        assert data["previous_version"] == "0.37.0"
    elif data["train"] == "0.37":
        assert data["previous_train"] == "0.36"
        assert data["previous_version"] == "0.36.0"
    elif data["train"] == "0.36":
        assert data["previous_train"] == "0.35"
        assert data["previous_version"] == "0.35.0"
    else:
        assert data["train"] in {"0.34", "0.35"}
        assert data["published_version"].startswith(data["train"] + ".")


def test_fleet_dispositions_stable_across_upgrade() -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    for name in ("hedron", "hedron-gradio", "hedron-mcp", "fastapi-workbench"):
        assert data[name]["disposition"] == "production_grade"


def test_present_034_remains_deferred_not_silently_supported() -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    assert "deferred" in data["present_034_status"]
    assert "default_presentation_gallery_refresh" in data["hedron-core"]["experimental"]
