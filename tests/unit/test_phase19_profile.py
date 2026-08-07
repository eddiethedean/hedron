"""Phase 0.19 PROFILE-019."""

from __future__ import annotations

from hedron_core.a11y import ACCESSIBILITY_PROFILE


def test_profile_pins_wcag_22_aria_12() -> None:
    p = ACCESSIBILITY_PROFILE
    assert p.wcag_version == "2.2"
    assert p.wcag_levels == ("A", "AA")
    assert p.wai_aria_version == "1.2"
    assert p.html_native_first is True
    assert p.apg_normative is False
    assert "WCAG 3" in p.experimental_drafts
    d = p.as_dict()
    assert d["claim_boundaries"]["forbids_auto_wcag_conformance"] is True
    assert d["claim_boundaries"]["empty_scan_is_not_accessible"] is True
