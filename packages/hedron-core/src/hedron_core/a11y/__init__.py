"""Accessibility engineering APIs for phase 0.19 (RFC-0023 / 0051–0055)."""

from __future__ import annotations

from hedron_core.a11y.contract import (
    REQUIRED_REVIEWED_CONTRACTS,
    AccessibilityContract,
    AccessibilityContractCatalog,
    contract_for_registered,
    default_contract,
    reviewed_contract,
    seed_reviewed_contracts,
)
from hedron_core.a11y.governance import (
    AccessibilityStatement,
    EvidenceInventory,
    HumanAtRecord,
    Waiver,
    refuse_auto_conformance_claim,
)
from hedron_core.a11y.profile import (
    ACCESSIBILITY_PROFILE,
    AccessibilityProfile,
    ClaimBoundary,
)
from hedron_core.a11y.scenario import (
    AccessibilityFinding,
    AccessibilityScenario,
    AccessibilityTreeNode,
    axe_to_sarif,
    snapshot_accessibility_tree,
)
from hedron_core.a11y.surfaces import (
    CognitivePreferences,
    MediaTrackContract,
    StructureReport,
    TargetSpacingPolicy,
    validate_page_structure,
)

__all__ = [
    "ACCESSIBILITY_PROFILE",
    "REQUIRED_REVIEWED_CONTRACTS",
    "AccessibilityContract",
    "AccessibilityContractCatalog",
    "AccessibilityFinding",
    "AccessibilityProfile",
    "AccessibilityScenario",
    "AccessibilityStatement",
    "AccessibilityTreeNode",
    "ClaimBoundary",
    "CognitivePreferences",
    "EvidenceInventory",
    "HumanAtRecord",
    "MediaTrackContract",
    "StructureReport",
    "TargetSpacingPolicy",
    "Waiver",
    "axe_to_sarif",
    "contract_for_registered",
    "default_contract",
    "refuse_auto_conformance_claim",
    "reviewed_contract",
    "seed_reviewed_contracts",
    "snapshot_accessibility_tree",
    "validate_page_structure",
]
