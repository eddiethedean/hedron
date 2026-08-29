"""Offline security posture report (POSTURE-056 / #553)."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Literal, cast

from hedron_core.compat import tomllib
from hedron_core.security_plane import CONFORMANCE_PROFILE_VERSION, SecurityPolicy

Confidence = Literal["proven", "heuristic", "application_owned", "unsupported", "unverifiable"]


@dataclass(frozen=True, slots=True)
class PostureFinding:
    id: str
    title: str
    severity: str
    confidence: Confidence
    ownership: str
    remediation: str
    evidence: str
    fingerprint: str


@dataclass
class PostureReport:
    profile_version: str
    policy_profile: str
    findings: list[PostureFinding] = field(default_factory=list[PostureFinding])
    unknowns: list[str] = field(default_factory=list[str])
    suppressions: list[dict[str, Any]] = field(default_factory=list[dict[str, Any]])
    baseline_drift: list[str] = field(default_factory=list[str])
    conformance_status: str = "unknown"

    def redacted_dict(self) -> dict[str, Any]:
        return {
            "profile_version": self.profile_version,
            "policy_profile": self.policy_profile,
            "findings": [asdict(item) for item in self.findings],
            "unknowns": list(self.unknowns),
            "suppressions": list(self.suppressions),
            "baseline_drift": list(self.baseline_drift),
            "conformance_status": self.conformance_status,
        }


def _load_suppressions(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.is_file():
        return []
    decoded: object = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(decoded, dict):
        rows: object = cast(dict[str, object], decoded).get("suppressions", [])
    else:
        rows = decoded
    if not isinstance(rows, list):
        return []
    return [cast(dict[str, Any], row) for row in cast(list[object], rows) if isinstance(row, dict)]


def _suppression_active(row: dict[str, Any], *, today: date) -> bool:
    expires = row.get("expires")
    if not expires:
        return True
    try:
        expiry = date.fromisoformat(str(expires))
    except ValueError:
        return False
    return expiry >= today


def collect_posture(
    *,
    project: Path,
    policy_name: str = "standard",
    suppressions_path: Path | None = None,
    baseline_path: Path | None = None,
    today: date | None = None,
) -> PostureReport:
    policy = SecurityPolicy.from_name(policy_name)
    findings: list[PostureFinding] = [
        PostureFinding(
            id="SEC-056-CSRF",
            title="CSRF enabled on active policy",
            severity="note" if policy.csrf_enabled else "error",
            confidence="proven",
            ownership="hedron-core",
            remediation="Keep csrf_enabled=True for mutating endpoints",
            evidence=(
                f"SecurityPolicy.profile={policy.profile.value} csrf_enabled={policy.csrf_enabled}"
            ),
            fingerprint="csrf-enabled",
        ),
        PostureFinding(
            id="SEC-056-CONFORM",
            title="Conformance profile version bound",
            severity="note",
            confidence="proven",
            ownership="hedron-conformance",
            remediation="Run security conformance profile in CI",
            evidence=policy.conformance_profile_version,
            fingerprint="conform-version",
        ),
    ]
    if policy.profile.value == "development" and policy.explorer_enabled:
        findings.append(
            PostureFinding(
                id="SEC-056-DEV-EXPLORER",
                title="Development Explorer enabled",
                severity="warning",
                confidence="proven",
                ownership="application",
                remediation="Do not deploy development profile to production",
                evidence="explorer_enabled=True",
                fingerprint="dev-explorer",
            )
        )
    unknowns = [
        "deployment WAF configuration (unverifiable offline)",
        "TLS termination and HSTS at the edge (unverifiable offline)",
    ]
    active_day = today or datetime.now(timezone.utc).date()
    suppressions = _load_suppressions(suppressions_path)
    active_suppressions = [
        row for row in suppressions if _suppression_active(row, today=active_day)
    ]
    expired = [row for row in suppressions if not _suppression_active(row, today=active_day)]
    suppressed_ids = {str(row.get("id", "")) for row in active_suppressions}
    visible = [finding for finding in findings if finding.id not in suppressed_ids]
    drift: list[str] = []
    if baseline_path and baseline_path.is_file():
        baseline_value: object = json.loads(baseline_path.read_text(encoding="utf-8"))
        baseline = (
            cast(dict[str, object], baseline_value) if isinstance(baseline_value, dict) else {}
        )
        fingerprints = baseline.get("fingerprints", [])
        baseline_fps = (
            {str(item) for item in cast(Sequence[object], fingerprints)}
            if isinstance(fingerprints, Sequence) and not isinstance(fingerprints, (str, bytes))
            else set[str]()
        )
        current_fps = {
            finding.fingerprint for finding in visible if finding.severity in {"error", "warning"}
        }
        drift = sorted(current_fps - baseline_fps)
    for row in expired:
        visible.append(
            PostureFinding(
                id=str(row.get("id", "EXPIRED")),
                title="Expired suppression",
                severity="error",
                confidence="proven",
                ownership=str(row.get("owner", "application")),
                remediation="Renew or remove the expired suppression",
                evidence=str(row.get("expires", "")),
                fingerprint=f"expired:{row.get('id', '')}",
            )
        )
    inventory = project / "docs" / "acceptance" / "security-control-inventory-056.toml"
    conformance_status = "unknown"
    if inventory.is_file():
        data = tomllib.loads(inventory.read_text(encoding="utf-8"))
        controls: object = data.get("control", [])
        dispositions = []
        if isinstance(controls, list):
            dispositions = [
                str(cast(dict[str, object], row).get("disposition", ""))
                for row in cast(list[object], controls)
                if isinstance(row, dict)
            ]
        if dispositions and all(d in {"covered", "tightened"} for d in dispositions):
            conformance_status = "inventory_complete"
        else:
            conformance_status = "inventory_partial"
    return PostureReport(
        profile_version=CONFORMANCE_PROFILE_VERSION,
        policy_profile=policy.profile.value,
        findings=visible,
        unknowns=unknowns,
        suppressions=active_suppressions,
        baseline_drift=drift,
        conformance_status=conformance_status,
    )


def report_to_sarif(report: PostureReport) -> dict[str, Any]:
    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "hedron-security-check",
                        "informationUri": "https://hedron.readthedocs.io/",
                        "rules": [
                            {
                                "id": finding.id,
                                "shortDescription": {"text": finding.title},
                                "fullDescription": {"text": finding.evidence},
                                "help": {"text": finding.remediation},
                                "properties": {
                                    "confidence": finding.confidence,
                                    "ownership": finding.ownership,
                                },
                            }
                            for finding in report.findings
                        ],
                    }
                },
                "results": [
                    {
                        "ruleId": finding.id,
                        "level": (
                            "error"
                            if finding.severity == "error"
                            else "warning"
                            if finding.severity == "warning"
                            else "note"
                        ),
                        "message": {"text": finding.title},
                        "properties": {"fingerprint": finding.fingerprint},
                    }
                    for finding in report.findings
                ],
            }
        ],
    }


def exit_code_for(
    report: PostureReport,
    *,
    strict: bool = False,
) -> int:
    errors = [f for f in report.findings if f.severity == "error" and f.confidence == "proven"]
    if errors:
        return 2
    if strict and report.baseline_drift:
        return 2
    if strict and any(
        f.severity == "warning" and f.confidence == "proven" for f in report.findings
    ):
        return 1
    return 0


def _cmd_security_check(args: argparse.Namespace) -> None:
    project = Path(args.project or ".").resolve()
    report = collect_posture(
        project=project,
        policy_name=args.policy,
        suppressions_path=Path(args.suppressions) if args.suppressions else None,
        baseline_path=Path(args.baseline) if args.baseline else None,
    )
    if args.format == "json":
        print(json.dumps(report.redacted_dict(), indent=2))
    elif args.format == "sarif":
        print(json.dumps(report_to_sarif(report), indent=2))
    else:
        print(f"hedron security-check ({report.policy_profile} / {report.profile_version})")
        print(f"conformance: {report.conformance_status}")
        for finding in report.findings:
            print(
                f"[{finding.severity}/{finding.confidence}] {finding.id}: {finding.title} "
                f"({finding.ownership})"
            )
            print(f"  evidence: {finding.evidence}")
            print(f"  remediation: {finding.remediation}")
        for unknown in report.unknowns:
            print(f"[unknown] {unknown}")
        if report.baseline_drift:
            print("baseline drift:")
            for item in report.baseline_drift:
                print(f"  - {item}")
    raise SystemExit(exit_code_for(report, strict=bool(args.strict)))


cmd_security_check = _cmd_security_check
