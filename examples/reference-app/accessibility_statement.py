"""GOVERN-019 dry-run statement for the reference app (no auto-conformance claims)."""

from __future__ import annotations

from hedron_core.a11y import (
    ACCESSIBILITY_PROFILE,
    AccessibilityStatement,
    EvidenceInventory,
)

__all__ = ["build_evidence_inventory", "build_statement"]


def build_evidence_inventory() -> EvidenceInventory:
    """Collect release-governance evidence placeholders for the reference app."""
    inventory = EvidenceInventory(
        profile_id=ACCESSIBILITY_PROFILE.profile_id,
        contracts=["Page", "Main", "Form", "DataTable", "DataEditor"],
        known_limitations=[
            "Charts and third-party embeds may require author-supplied text alternatives.",
            "Human screen-reader evaluation is owned by Hedron 0.21 (D-052); "
            "protocol under docs/acceptance/human-at/ — sessions not yet Verified.",
        ],
        third_party_boundaries=["Plotly/Altair runtimes when hedron[charts] is installed"],
        feedback_route="mailto:security@example.invalid",
        automation_results=[
            {
                "gate": "AT-019",
                "note": "Playwright/axe matrix in Hedron CI; empty scan is never 'accessible'",
            }
        ],
        # human_at_results stays empty until SR-021 / PARTICIPANT-021 execute.
    )
    return inventory


def build_statement() -> AccessibilityStatement:
    """Human-approved statement template — does not claim WCAG conformance."""
    return AccessibilityStatement(
        scope="examples/reference-app local demo only",
        contact="Hedron maintainers",
        feedback_route="https://github.com/eddiethedean/hedron/issues",
        known_limitations=[
            "Demo credentials and in-memory backends are not production-ready.",
            "Automated axe scans are incomplete without human AT review "
            "(0.21 D-052 packet Refined / Planned; see docs/acceptance/human-at/).",
        ],
        alternatives=["Full-page no-JS form POST paths where forms are demonstrated"],
        tested_environments=[
            "Chromium / Firefox / WebKit via Hedron browser CI when HEDRON_BROWSER=1",
        ],
        assessment_approach=(
            "Hedron AccessibilityContract + AT-019 automation; human SR owned by 0.21 "
            "(D-052) — not yet Verified"
        ),
    )


if __name__ == "__main__":
    inv = build_evidence_inventory().as_dict()
    stmt = build_statement()
    stmt.approved_by = "reference-app maintainer (dry-run)"
    print({"inventory": inv, "statement": stmt.export()})
