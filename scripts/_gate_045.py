"""Shared constants and contract helpers for the phase 0.45 gate."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.45.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "ecosystem-capability-inventory-045.toml"
PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_45.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-045.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "TYPED_INTERACTION_ECOSYSTEM_045.md"
API = ROOT / "docs" / "api" / "INTERACTION_CATALOG.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0072-TYPED-INTERACTION-ECOSYSTEM.md"
CATALOG_ENTRY = ROOT / "docs" / "acceptance" / "catalog-entry-045.toml"
MANIFEST_FORMAT = ROOT / "docs" / "acceptance" / "manifest-format-045.toml"
HOST_FACTS = ROOT / "docs" / "acceptance" / "host-portable-facts-045.toml"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
STATUS = ROOT / "STATUS.md"
RELEASE = ROOT / "docs" / "release.toml"
PYPROJECT = ROOT / "pyproject.toml"

PACKET_FILES = (
    GATE,
    INVENTORY,
    PACKET,
    UPGRADE,
    IMPLEMENTATION,
    API,
    RFC,
    CATALOG_ENTRY,
    MANIFEST_FORMAT,
    HOST_FACTS,
)

EXPECTED_GATES = (
    "CATALOG-045",
    "MANIFEST-045",
    "PROJECTION-045",
    "HOST-045",
    "AUTHOR-045",
    "SURFACE-045",
    "REMOTE-045",
    "TOOLING-045",
    "PORTABLE-045",
    "DEPLOY-045",
    "SECURITY-045",
    "A11Y-045",
    "BROWSER-045",
    "COMPAT-045",
    "PERF-045",
    "DOCS-045",
    "REGRESS-045",
    "PKG-045",
)
EXPECTED_REQUIREMENT_RANGES = (
    "EC-CAT-001..010",
    "EC-MAN-001..010",
    "EC-PROJ-001..010",
    "EC-HOST-001..008",
    "EC-AUTHOR-001..008",
    "EC-SURFACE-001..008",
    "EC-REMOTE-001..008",
    "EC-TOOL-001..010",
    "EC-PORT-001..009",
    "EC-DEPLOY-001..007",
    "EC-SEC-001..010",
    "EC-A11Y-001..006",
    "EC-QUAL-001..006",
    "EC-QUAL-007..008",
    "EC-QUAL-009",
    "EC-QUAL-010",
    "EC-QUAL-011..012",
)

FROZEN_CONTRACT_MARKERS = (
    "ViewParams",
    "FormBody",
    "hedron.type",
    "OutcomeMap(case(",
    "BindingAdapter",
    "descriptor_fingerprint",
)


def accepted_contract_present() -> bool:
    rfc = RFC.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    return "**Status:** Accepted" in rfc and "| D-074 | Accepted |" in decisions


def contract_refine_present() -> bool:
    decisions = DECISIONS.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (RFC, IMPLEMENTATION, API, PACKET)
    )
    return "| D-077 | Accepted |" in decisions and all(
        marker in combined for marker in FROZEN_CONTRACT_MARKERS
    )


def require_files(paths: list[Path], errors: list[str]) -> None:
    for path in paths:
        if not path.is_file():
            errors.append(f"missing required file: {path}")


def gate_state(gate_id: str) -> str | None:
    data = tomllib.loads(GATE.read_text(encoding="utf-8"))
    for row in data.get("evidence") or []:
        if row.get("id") == gate_id:
            return str(row.get("state", "")).strip()
    return None
