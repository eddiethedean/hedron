"""Workflow contract manifest, reason codes, budgets, and upgrade reports (0.55)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal, cast

SCHEMA_VERSION = "hedron-workflow-manifest-1"
UPGRADE_SCHEMA_VERSION = "hedron-upgrade-report-1"

ReasonCode = Literal[
    "allowed",
    "denied",
    "hidden",
    "disabled",
    "replayed",
    "rejected",
    "uploaded",
    "conflict",
]

REASON_CODES: tuple[ReasonCode, ...] = (
    "allowed",
    "denied",
    "hidden",
    "disabled",
    "replayed",
    "rejected",
    "uploaded",
    "conflict",
)


@dataclass(frozen=True, slots=True)
class WorkflowBudget:
    body_bytes: int = 1_048_576
    field_count: int = 64
    filename_bytes: int = 255
    report_bytes: int = 8_192
    replay_keys: int = 10_000
    concurrency: int = 32
    retention_seconds: int = 86_400
    cleanup_timeout_seconds: int = 30


@dataclass(frozen=True, slots=True)
class WorkflowManifest:
    """Redacted, versioned inspection model for Explorer/CLI/upgrade report."""

    schema_version: str = SCHEMA_VERSION
    app_id: str = "app"
    layout_regions: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    action_safety: dict[str, str] = field(default_factory=dict[str, str])
    upload_requirements: dict[str, object] = field(default_factory=dict[str, object])
    security_headers: dict[str, object] = field(default_factory=dict[str, object])
    migration_status: str = "legacy"
    budgets: WorkflowBudget = field(default_factory=WorkflowBudget)
    reason_codes: tuple[ReasonCode, ...] = REASON_CODES

    def redacted_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "app_id": self.app_id,
            "layout_regions": list(self.layout_regions),
            "capabilities": list(self.capabilities),
            "action_safety": dict(self.action_safety),
            "upload_requirements": dict(self.upload_requirements),
            "security_headers": {
                k: v for k, v in self.security_headers.items() if k not in {"raw_csp", "secrets"}
            },
            "migration_status": self.migration_status,
            "budgets": asdict(self.budgets),
            "reason_codes": list(self.reason_codes),
        }


@dataclass(frozen=True, slots=True)
class UpgradeFinding:
    kind: Literal["definite", "heuristic"]
    code: str
    message: str
    source: str | None = None


@dataclass(frozen=True, slots=True)
class UpgradeReport:
    schema_version: str = UPGRADE_SCHEMA_VERSION
    from_version: str = "0.54.0"
    to_version: str = "0.55.0"
    findings: tuple[UpgradeFinding, ...] = ()
    offline: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "from_version": self.from_version,
            "to_version": self.to_version,
            "offline": self.offline,
            "findings": [asdict(f) for f in self.findings],
        }

    def exit_code(self, *, fail_on_definite: bool = True) -> int:
        if any(f.kind == "definite" for f in self.findings) and fail_on_definite:
            return 2
        return 0


def build_upgrade_report(
    *,
    from_version: str,
    to_version: str,
    manifest: WorkflowManifest | None = None,
    baseline: dict[str, Any] | None = None,
) -> UpgradeReport:
    """Offline contract diff — never contacts external services."""
    findings: list[UpgradeFinding] = []
    if not from_version.startswith("0."):
        findings.append(
            UpgradeFinding(
                kind="definite",
                code="HED-UPGRADE-0001",
                message=f"Unsupported from_version {from_version!r}",
                source="cli",
            )
        )
    if baseline is not None:
        schema = baseline.get("schema_version")
        if schema not in {None, UPGRADE_SCHEMA_VERSION, SCHEMA_VERSION}:
            findings.append(
                UpgradeFinding(
                    kind="definite",
                    code="HED-UPGRADE-0002",
                    message="Stale or incompatible reviewed baseline schema",
                    source="baseline",
                )
            )
    if manifest is not None and manifest.migration_status == "legacy":
        findings.append(
            UpgradeFinding(
                kind="heuristic",
                code="HED-UPGRADE-1001",
                message="Application still on legacy workflow compatibility mode",
                source="manifest.migration_status",
            )
        )
    if from_version.startswith("0.54") and to_version.startswith("0.55"):
        findings.append(
            UpgradeFinding(
                kind="heuristic",
                code="HED-UPGRADE-1002",
                message="New 0.55 APIs are opt-in beta; declare workflow_055 to enable",
                source="docs/acceptance/upgrade-fixtures-055.md",
            )
        )
    return UpgradeReport(
        from_version=from_version,
        to_version=to_version,
        findings=tuple(findings),
        offline=True,
    )


def load_baseline(path: Path) -> dict[str, Any]:
    data: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Baseline must be a JSON object")
    return cast(dict[str, Any], data)


upgrade_report_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": UPGRADE_SCHEMA_VERSION,
    "type": "object",
    "required": ["schema_version", "from_version", "to_version", "findings", "offline"],
    "properties": {
        "schema_version": {"const": UPGRADE_SCHEMA_VERSION},
        "from_version": {"type": "string"},
        "to_version": {"type": "string"},
        "offline": {"const": True},
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["kind", "code", "message"],
                "properties": {
                    "kind": {"enum": ["definite", "heuristic"]},
                    "code": {"type": "string"},
                    "message": {"type": "string"},
                    "source": {"type": ["string", "null"]},
                },
            },
        },
    },
}

__all__ = [
    "REASON_CODES",
    "SCHEMA_VERSION",
    "UPGRADE_SCHEMA_VERSION",
    "ReasonCode",
    "UpgradeFinding",
    "UpgradeReport",
    "WorkflowBudget",
    "WorkflowManifest",
    "build_upgrade_report",
    "load_baseline",
    "upgrade_report_schema",
]
