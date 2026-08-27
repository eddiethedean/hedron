"""Edron 0.7 to 0.8 deployment upgrade evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from edron.deployment import PROFILE_NAMES

ROOT = Path(__file__).resolve().parents[2]


def test_phase08_packet_and_all_profiles_are_present() -> None:
    packet = (ROOT / "docs/acceptance/EDRON_008.md").read_text(encoding="utf-8")
    gates = tomllib.loads((ROOT / "docs/acceptance/edron-phase08.toml").read_text(encoding="utf-8"))
    assert "edron>=0.8,<0.9" in packet or "0.8.0" in packet
    assert gates["phase"] == "0.8"
    assert gates["status"] == "Implemented"
    assert {row["id"] for row in gates["gate"]} == {
        "EDR-08-PROFILE",
        "EDR-08-EDGE",
        "EDR-08-HOST",
        "EDR-08-OPS",
        "EDR-08-SUPPLY",
        "EDR-08-UPGRADE",
        "EDR-08-REGRESSION",
    }
    assert set(PROFILE_NAMES) == {
        "local",
        "single-process",
        "reverse-proxy",
        "container",
        "orchestrated",
        "workbench",
        "posit-connect",
    }


def test_generated_projects_use_the_current_09_train() -> None:
    scaffold = (ROOT / "packages/edron/src/edron/scaffolds.py").read_text(encoding="utf-8")
    generated = (ROOT / "packages/edron/src/edron/migrate/generate.py").read_text(encoding="utf-8")
    project = (ROOT / "packages/edron/pyproject.toml").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs/EDRON_ROADMAP.md").read_text(encoding="utf-8")
    assert "edron>=0.9,<0.10" in scaffold
    assert "edron>=0.9,<0.10" in generated
    assert "edron>=0.8,<0.9" not in scaffold + generated
    assert '"hedron>=0.67.0,<0.68"' in project
    assert '"hedron-data>=0.67.0,<0.68"' in project
    assert "0.9.0` target train is Hedron `0.67.0" in roadmap
