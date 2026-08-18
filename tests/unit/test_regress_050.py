"""REGRESS-050 fleet + authoring; EXPLORER-10-001 stays Deferred."""

from __future__ import annotations

from pathlib import Path

from tests.unit.test_authoring_050 import test_hx_trigger_include_validate_and_rejects_js_vals
from tests.unit.test_compat_050 import test_049_form_and_actionhandle_still_work


def test_authoring_and_compat_still_green() -> None:
    from tests.unit._helpers_050 import reset_050

    reset_050()
    test_hx_trigger_include_validate_and_rejects_js_vals()
    test_049_form_and_actionhandle_still_work()


def test_explorer_10_001_remains_deferred() -> None:
    inventory = Path("docs/acceptance/explorer-capability-inventory-050.toml").read_text(
        encoding="utf-8"
    )
    assert "explorer-10-001-live-traces" in inventory
    assert 'state = "Excluded"' in inventory
    packet = Path("docs/acceptance/RELEASE_0_50.md").read_text(encoding="utf-8")
    assert "EXPLORER-10-001" in packet
