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
    train = str(data["train"])
    published = str(data["published_version"])
    previous_train = str(data["previous_train"])
    previous_version = str(data["previous_version"])
    assert published.startswith(f"{train}.")
    assert previous_version.startswith(f"{previous_train}.")
    # Living tip must stay ahead of the 0.34→0.35 upgrade inventory this file owns.
    major_minor = tuple(int(p) for p in train.split(".")[:2])
    assert major_minor >= (0, 34)


def test_fleet_dispositions_stable_across_upgrade() -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    for name in ("hedron", "hedron-gradio", "hedron-mcp", "fastapi-workbench"):
        assert data[name]["disposition"] == "production_grade"


def test_present_034_remains_deferred_not_silently_supported() -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    assert "deferred" in data["present_034_status"]
    assert "default_presentation_gallery_refresh" in data["hedron-core"]["experimental"]
