"""Edron 1.0 acceptance and direct Hedron 1.0 dependency contract."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_edron_100_packet_requires_the_canonical_hedron_train() -> None:
    packet = (ROOT / "docs/acceptance/EDRON_100.md").read_text(encoding="utf-8")
    gates = tomllib.loads((ROOT / "docs/acceptance/edron-100.toml").read_text(encoding="utf-8"))

    assert "edron==1.0.0" in packet
    assert "Hedron `1.0.0`" in packet
    assert gates["release"] == "1.0"
    assert gates["version"] == "1.0.0"
    assert gates["hedron_train"] == "1.0.0"
    assert gates["hedron_requirement"] == ">=1.0.0,<2.0"
    assert gates["hedron_data_requirement"] == ">=1.0.0,<2.0"
    assert gates["canonical_roles"] == ["page", "view", "action", "include"]
    assert all(row["state"] == "Implemented" for row in gates["gate"])


def test_edron_runtime_does_not_reimplement_hedron_route_handles() -> None:
    source = (ROOT / "packages/edron/src/edron/app.py").read_text(encoding="utf-8")
    for forbidden in (
        "build_view_handle",
        "build_command_handle",
        "self.hedron._root_router",
        "self.hedron._sync_root_route",
    ):
        assert forbidden not in source


def test_edron_metadata_and_generated_projects_require_1_x() -> None:
    project = tomllib.loads((ROOT / "packages/edron/pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]
    assert project["version"] == "1.0.0"
    assert "hedron>=1.0.0,<2.0" in project["dependencies"]
    assert "hedron-data>=1.0.0,<2.0" in project["dependencies"]

    for relative in (
        "packages/edron/src/edron/scaffolds.py",
        "packages/edron/src/edron/migrate/generate.py",
    ):
        generated = (ROOT / relative).read_text(encoding="utf-8")
        assert '"edron>=1.0.0,<2.0"' in generated
        assert '"hedron>=1.0.0,<2.0"' in generated
        assert '"hedron-data>=1.0.0,<2.0"' in generated
