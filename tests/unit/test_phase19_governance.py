"""Phase 0.19 GOVERN-019."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from hedron_core.a11y import (
    AccessibilityStatement,
    EvidenceInventory,
    HumanAtRecord,
    Waiver,
    refuse_auto_conformance_claim,
)
from hedron_core.diagnostics import HedronError


def test_waiver_requires_fields_and_blocks_expired() -> None:
    today = datetime.now(UTC).date()
    w = Waiver(
        id="W1",
        owner="a11y-owners",
        rationale="third-party chart",
        affected_users="color-blind users for legend",
        remediation="add tabular fallback",
        expires=today + timedelta(days=30),
        component="Chart",
    )
    assert w.validated().id == "W1"
    expired = Waiver(
        id="W0",
        owner="a11y-owners",
        rationale="x",
        affected_users="y",
        remediation="z",
        expires=today - timedelta(days=1),
    )
    with pytest.raises(HedronError) as exc:
        expired.validated()
    assert exc.value.diagnostic.code == "HED-A11Y-0010"


def test_refuse_auto_claims_and_statement_export() -> None:
    with pytest.raises(HedronError) as exc:
        refuse_auto_conformance_claim("wcag")
    assert exc.value.diagnostic.code == "HED-A11Y-0011"
    inv = EvidenceInventory(feedback_route="a11y@example.test")
    inv.contracts.append("Button")
    inv.known_limitations.append("Human AT deferred to 0.21")
    assert inv.as_dict()["feedback_route"] == "a11y@example.test"
    assert inv.as_dict()["human_at_results"] == []
    stmt = AccessibilityStatement(
        scope="reference-app",
        contact="a11y@example.test",
        feedback_route="mailto:a11y@example.test",
        tested_environments=["Playwright Chromium/Firefox/WebKit"],
        approved_by="release-manager",
    )
    exported = stmt.export()
    assert exported["conformance_claim"] is None
    assert exported["vpat_acr"] is None
    with pytest.raises(HedronError):
        AccessibilityStatement(scope="x").export()


def test_human_at_record_round_trip_and_rejects_pii_flag() -> None:
    payload = {
        "record_id": "hat-test-0001",
        "gate_ids": ["SR-021", "ARTIFACT-021"],
        "combo_id": "vo-safari-macos",
        "os": {"name": "macOS", "version": "15.0"},
        "browser": {"name": "Safari", "version": "18.0"},
        "at": {"name": "VoiceOver", "version": "bundled"},
        "task_id": "login",
        "result": "placeholder",
        "owner": "hedron-maintainers",
        "retest_date": "2099-01-01",
        "redacted": True,
    }
    record = HumanAtRecord.from_dict(payload)
    inv = EvidenceInventory()
    inv.add_human_at(record)
    assert inv.as_dict()["human_at_results"][0]["record_id"] == "hat-test-0001"
    with pytest.raises(ValueError, match="redacted"):
        HumanAtRecord.from_dict({**payload, "redacted": False})
