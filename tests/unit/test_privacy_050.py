"""PRIVACY-050 redaction and REV-026-003 accepted risk."""

from __future__ import annotations

from pathlib import Path

from hedron_explorer.services.runtime import redact
from hedron_explorer.services.simulation import redacted_app_scenario


def test_redact_paths() -> None:
    assert redact("/tmp/secret/token.hdj") == "token.hdj"


def test_scenario_export_has_no_auth() -> None:
    payload = redacted_app_scenario(route="/", ok=True)
    assert payload["auth"] is None
    assert payload["redacted"] is True


def test_rev_026_003_stays_accepted_risk() -> None:
    text = Path("docs/acceptance/RELEASE_0_50.md").read_text(encoding="utf-8")
    assert "REV-026-003" in text
    assert "accepted risk" in text.lower() or "stays accepted" in text.lower()
