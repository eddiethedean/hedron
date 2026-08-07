"""Waiver, evidence inventory, and statement template (GOVERN-019)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any, Literal

from hedron_core.a11y.profile import ACCESSIBILITY_PROFILE
from hedron_core.diagnostics import error

__all__ = [
    "AccessibilityStatement",
    "EvidenceInventory",
    "Waiver",
    "refuse_auto_conformance_claim",
]


@dataclass(frozen=True, slots=True)
class Waiver:
    """Structured accessibility waiver (replaces free-form chart waiver strings)."""

    id: str
    owner: str
    rationale: str
    affected_users: str
    remediation: str
    expires: date
    criterion: str | None = None
    component: str | None = None

    def validated(self, *, today: date | None = None) -> Waiver:
        if not self.id.strip() or not self.owner.strip():
            raise ValueError("Waiver requires id and owner")
        if not self.rationale.strip() or not self.affected_users.strip():
            raise ValueError("Waiver requires rationale and affected_users")
        if not self.remediation.strip():
            raise ValueError("Waiver requires remediation")
        check = today or date.today()
        if self.expires < check:
            raise error(
                "HED-A11Y-0010",
                title="Expired accessibility waiver",
                explanation=f"Waiver {self.id!r} expired on {self.expires.isoformat()}.",
                remediation="Renew with owner approval or remediate the gap.",
            )
        return self

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "owner": self.owner,
            "rationale": self.rationale,
            "affected_users": self.affected_users,
            "remediation": self.remediation,
            "expires": self.expires.isoformat(),
            "criterion": self.criterion,
            "component": self.component,
        }


def refuse_auto_conformance_claim(
    kind: Literal["wcag", "legal", "certification", "vpat", "acr", "accessible"],
) -> None:
    """Raise when callers attempt automatic conformance / legal claims."""
    raise error(
        "HED-A11Y-0011",
        title="Automatic accessibility claim refused",
        explanation=(
            f"Hedron refuses to emit automatic {kind!r} claims "
            f"(profile {ACCESSIBILITY_PROFILE.profile_id})."
        ),
        remediation="Publish a human-approved scoped statement from AccessibilityStatement.",
    )


@dataclass
class EvidenceInventory:
    """Collect contract, automation, and waiver evidence for release governance."""

    profile_id: str = ACCESSIBILITY_PROFILE.profile_id
    contracts: list[str] = field(default_factory=list)
    automation_results: list[dict[str, Any]] = field(default_factory=list)
    waivers: list[Waiver] = field(default_factory=list)
    known_limitations: list[str] = field(default_factory=list)
    third_party_boundaries: list[str] = field(default_factory=list)
    feedback_route: str | None = None
    generated_at: str = field(
        default_factory=lambda: datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    def add_waiver(self, waiver: Waiver, *, today: date | None = None) -> None:
        self.waivers.append(waiver.validated(today=today))

    def as_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "contracts": list(self.contracts),
            "automation_results": list(self.automation_results),
            "waivers": [w.as_dict() for w in self.waivers],
            "known_limitations": list(self.known_limitations),
            "third_party_boundaries": list(self.third_party_boundaries),
            "feedback_route": self.feedback_route,
            "generated_at": self.generated_at,
        }


@dataclass
class AccessibilityStatement:
    """Human-approved statement template fields — never auto-claims conformance."""

    standard: str = f"WCAG {ACCESSIBILITY_PROFILE.wcag_version} Level AA (scoped)"
    scope: str = ""
    contact: str = ""
    feedback_route: str = ""
    known_limitations: list[str] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)
    tested_environments: list[str] = field(default_factory=list)
    assessment_approach: str = "Hedron automation + human review"
    assessment_date: str = field(default_factory=lambda: date.today().isoformat())
    approved_by: str | None = None

    def export(self) -> dict[str, Any]:
        if not self.approved_by:
            raise error(
                "HED-A11Y-0012",
                title="Accessibility statement requires human approval",
                explanation="approved_by is required before export.",
                remediation="Record the approving reviewer name or role.",
            )
        return {
            "standard": self.standard,
            "scope": self.scope,
            "contact": self.contact,
            "feedback_route": self.feedback_route,
            "known_limitations": list(self.known_limitations),
            "alternatives": list(self.alternatives),
            "tested_environments": list(self.tested_environments),
            "assessment_approach": self.assessment_approach,
            "assessment_date": self.assessment_date,
            "approved_by": self.approved_by,
            "conformance_claim": None,
            "legal_compliance_claim": None,
            "vpat_acr": None,
        }
