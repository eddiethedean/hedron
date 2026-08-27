"""Phase 0.9 native Hedron 0.67 contracts."""

from __future__ import annotations

from pathlib import Path

import edron as ed
import hedron
from edron.deprecations import DEPRECATED_HEDRON_067_PATHS, deprecated_hedron_paths
from edron.scaffolds import create_scaffold


def test_public_contract_is_the_native_hedron_contract() -> None:
    assert ed.Interaction is hedron.Interaction
    assert ed.Outcome is hedron.Outcome
    local = ed.Interaction.local("toggle", state_keys=("open",))
    request = ed.Interaction.request("home-status")
    combined = ed.Interaction.combined("toggle", "home-status", state_keys=("open",))
    assert local.kind is ed.InteractionKind.LOCAL
    assert request.kind is ed.InteractionKind.REQUEST
    assert combined.kind is ed.InteractionKind.COMBINED
    assert local.demands()[0].feature == "interaction"
    assert request.demands() == ()


def test_browser_plan_is_demand_driven_and_native() -> None:
    off = ed.browser_plan()
    on = ed.browser_plan((ed.feature_demand("morph", "Home"),))
    closure = ed.browser_closure(off, fragments=(("status", on),))
    assert isinstance(off, hedron.BrowserFeaturePlan)
    assert off.feature_off is True
    assert on.requires("morph") is True
    assert "/hedron-static/alpine/csp-3.16.3.js" in on.assets
    assert closure.fragment("status") == on


def test_app_records_interactions_for_explanation() -> None:
    app = ed.App(title="Phase 0.9", session_secret="test")
    interaction = app.interaction(ed.Interaction.local("toggle", state_keys=("open",)))
    facts = app.explain()
    assert facts["interactions"] == [interaction.to_dict()]
    assert facts["browser_contract"]["hedron_train"] == "0.67.0"


def test_scaffold_pins_edron_and_hedron_067(tmp_path: Path) -> None:
    create_scaffold("Phase 0.9", tmp_path / "app")
    project = (tmp_path / "app" / "pyproject.toml").read_text(encoding="utf-8")
    assert '"edron>=0.9,<0.10"' in project
    assert '"hedron>=0.67.0,<0.68"' in project
    assert '"hedron-data>=0.67.0,<0.68"' in project


def test_deprecated_paths_are_migration_only_markers() -> None:
    assert deprecated_hedron_paths("safe generated output") == ()
    assert "hedron-dialog" in DEPRECATED_HEDRON_067_PATHS
    assert deprecated_hedron_paths("migration: hedron-dialog") == ("hedron-dialog",)
