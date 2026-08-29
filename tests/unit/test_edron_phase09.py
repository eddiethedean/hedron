"""Historical Phase 0.9 contracts plus the Edron 1.0 train cutover."""

from __future__ import annotations

from pathlib import Path

import edron as ed
import hedron
from edron.deprecations import DEPRECATED_HEDRON_067_PATHS, deprecated_hedron_paths
from edron.scaffolds import create_scaffold


def test_public_contract_is_the_native_hedron_contract() -> None:
    assert ed.Interaction is hedron.Interaction
    assert ed.Outcome is hedron.Outcome
    local = ed.Interaction.local("toggle", state_keys=("open",), state={"open": False})
    request = ed.Interaction.request("home-status")
    combined = ed.Interaction.combined(
        "toggle", "home-status", state_keys=("open",), state={"open": False}
    )
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
    interaction = app.interaction(
        ed.Interaction.local("toggle", state_keys=("open",), state={"open": False})
    )
    facts = app.explain()
    assert facts["interactions"] == [interaction.to_dict()]
    assert facts["browser_contract"]["hedron_train"] == "1.0.0"
    assert facts["browser_contract"]["canonical_roles"] == (
        "page",
        "view",
        "action",
        "include",
    )


def test_scaffold_requires_the_edron_and_hedron_1_0_trains(tmp_path: Path) -> None:
    create_scaffold("Edron 1.0", tmp_path / "app")
    project = (tmp_path / "app" / "pyproject.toml").read_text(encoding="utf-8")
    assert '"edron>=1.0.0,<2.0"' in project
    assert '"hedron>=1.0.0,<2.0"' in project
    assert '"hedron-data>=1.0.0,<2.0"' in project


def test_deprecated_paths_are_migration_only_markers() -> None:
    assert deprecated_hedron_paths("safe generated output") == ()
    assert "hedron-dialog" in DEPRECATED_HEDRON_067_PATHS
    assert deprecated_hedron_paths("migration: hedron-dialog") == ("hedron-dialog",)
