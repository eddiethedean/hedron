"""Shared constants and contract helpers for the phase 0.43 gate."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.43.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "interaction-capability-inventory-043.toml"
PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_43.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-043.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "INTERACTION_HANDLES_043.md"
API = ROOT / "docs" / "api" / "REFRESHABLE_VIEWS.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0070-REFRESHABLE-VIEWS.md"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
STATUS = ROOT / "STATUS.md"
RELEASE = ROOT / "docs" / "release.toml"
PYPROJECT = ROOT / "pyproject.toml"

PACKET_FILES = (GATE, INVENTORY, PACKET, UPGRADE, IMPLEMENTATION, API, RFC)
EXPECTED_GATES = (
    "VIEW-043",
    "COMMAND-043",
    "UPDATE-043",
    "SECURITY-043",
    "A11Y-043",
    "BROWSER-043",
    "TOOLING-043",
    "COMPAT-043",
    "PERF-043",
    "DOCS-043",
    "REGRESS-043",
    "PKG-043",
)
EXPECTED_REQUIREMENT_RANGES = (
    "IH-VIEW-001..009",
    "IH-BIND-001..006",
    "IH-CMD-001..007",
    "IH-REFRESH-001..007",
    "IH-PATCH-001..008",
    "IH-HOST-001..007",
    "IH-HOST-002..006",
    "IH-SEC-001..007",
    "IH-DX-001..007",
    "IH-EXT-001..007",
    "IH-QUAL-001..004",
    "IH-QUAL-005..007",
    "IH-QUAL-008",
    "IH-QUAL-009",
)


def accepted_contract_present() -> bool:
    rfc = RFC.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    return "**Status:** Accepted" in rfc and "| D-071 | Accepted |" in decisions


def cross_phase_refinement_present() -> bool:
    decisions = DECISIONS.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (RFC, IMPLEMENTATION, API, PACKET)
    )
    return "| D-073 | Accepted |" in decisions and all(
        marker in combined
        for marker in (
            "FragmentHandle[Bind, Content]",
            "ActionHandle[Input, Result]",
            "structural binding",
            "dynamic/observed",
        )
    )
