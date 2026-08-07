"""Versioned accessibility standards profile (PROFILE-019)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

__all__ = ["ACCESSIBILITY_PROFILE", "AccessibilityProfile", "ClaimBoundary"]


@dataclass(frozen=True, slots=True)
class ClaimBoundary:
    """Explicit non-goals for framework-generated accessibility claims."""

    forbids_auto_wcag_conformance: bool = True
    forbids_auto_legal_compliance: bool = True
    forbids_auto_certification: bool = True
    forbids_auto_vpat_acr: bool = True
    empty_scan_is_not_accessible: bool = True


@dataclass(frozen=True, slots=True)
class AccessibilityProfile:
    """Pinned normative baseline for Hedron accessibility engineering."""

    profile_id: str = "hedron-a11y-0.19"
    wcag_version: str = "2.2"
    wcag_levels: tuple[Literal["A", "AA"], ...] = ("A", "AA")
    wai_aria_version: str = "1.2"
    accessible_name_version: str = "1.2"
    atag_version: str = "2.0"
    html_native_first: bool = True
    apg_normative: bool = False
    experimental_drafts: tuple[str, ...] = ("WAI-ARIA 1.3", "WCAG 3")
    claim_boundaries: ClaimBoundary = field(default_factory=ClaimBoundary)
    act_rules_pin: str = "act-rules:2024-06 (WCAG 2.2 A/AA subset; pin at release)"
    axe_engine_pin: str = "axe-playwright-python>=0.1.4 (axe-core via package)"

    def as_dict(self) -> dict[str, object]:
        return {
            "profile_id": self.profile_id,
            "wcag_version": self.wcag_version,
            "wcag_levels": list(self.wcag_levels),
            "wai_aria_version": self.wai_aria_version,
            "accessible_name_version": self.accessible_name_version,
            "atag_version": self.atag_version,
            "html_native_first": self.html_native_first,
            "apg_normative": self.apg_normative,
            "experimental_drafts": list(self.experimental_drafts),
            "claim_boundaries": {
                "forbids_auto_wcag_conformance": (
                    self.claim_boundaries.forbids_auto_wcag_conformance
                ),
                "forbids_auto_legal_compliance": (
                    self.claim_boundaries.forbids_auto_legal_compliance
                ),
                "forbids_auto_certification": self.claim_boundaries.forbids_auto_certification,
                "forbids_auto_vpat_acr": self.claim_boundaries.forbids_auto_vpat_acr,
                "empty_scan_is_not_accessible": self.claim_boundaries.empty_scan_is_not_accessible,
            },
            "act_rules_pin": self.act_rules_pin,
            "axe_engine_pin": self.axe_engine_pin,
        }


ACCESSIBILITY_PROFILE = AccessibilityProfile()
