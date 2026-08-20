"""Waiver, evidence inventory, and statement template (GOVERN-019 / 0.21 human AT)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any, Literal

from hedron_core.a11y.profile import ACCESSIBILITY_PROFILE
from hedron_core.diagnostics import error

__all__ = [
    "AccessibilityStatement",
    "EvidenceInventory",
    "HumanAtRecord",
    "Waiver",
    "refuse_auto_conformance_claim",
]

_COMBO_IDS = frozenset(
    {
        "vo-safari-macos",
        "nvda-firefox-windows",
        "talkback-chromium-android",
        "stretch-other",
    }
)
_TASK_IDS = frozenset(
    {
        "login",
        "crud-form-pe",
        "crud-form-htmx",
        "fragment-refresh",
        "data-editor-smoke",
    }
)
_RESULTS = frozenset({"pass", "fail", "blocked", "incomplete", "placeholder"})
_SEVERITIES = frozenset({"blocker", "major", "minor", "note", "none"})
_PARTICIPANT_CATEGORIES = frozenset(
    {"screen_reader", "motor", "low_vision", "cognitive", "maintainer_sr"}
)
_GATE_IDS = frozenset(
    {
        "PROTOCOL-021",
        "SR-021",
        "PARTICIPANT-021",
        "ARTIFACT-021",
        "REMEDIATE-021",
    }
)


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


@dataclass(frozen=True, slots=True)
class HumanAtRecord:
    """Redacted human AT ledger row (0.21 / D-052). Never holds participant PII."""

    record_id: str
    gate_ids: tuple[str, ...]
    combo_id: str
    os_name: str
    os_version: str
    browser_name: str
    browser_version: str
    at_name: str
    at_version: str
    task_id: str
    result: str
    owner: str
    retest_date: str
    redacted: bool = True
    stretch: bool = False
    session_id: str | None = None
    participant_category: str | None = None
    at_settings: str | None = None
    task_ids: tuple[str, ...] = ()
    severity: str = "none"
    known_issue: str = ""
    issue_url: str | None = None
    waiver_id: str | None = None
    notes: str = ""

    def validated(self) -> HumanAtRecord:
        if not self.record_id.strip() or not self.owner.strip():
            raise ValueError("HumanAtRecord requires record_id and owner")
        if not self.redacted:
            raise ValueError("HumanAtRecord.redacted must be True (no PII in public rows)")
        if self.combo_id not in _COMBO_IDS:
            raise ValueError(f"Unknown combo_id: {self.combo_id!r}")
        if self.task_id not in _TASK_IDS:
            raise ValueError(f"Unknown task_id: {self.task_id!r}")
        if self.result not in _RESULTS:
            raise ValueError(f"Unknown result: {self.result!r}")
        if self.severity not in _SEVERITIES:
            raise ValueError(f"Unknown severity: {self.severity!r}")
        if self.participant_category is not None and (
            self.participant_category not in _PARTICIPANT_CATEGORIES
        ):
            raise ValueError(f"Unknown participant_category: {self.participant_category!r}")
        bad_gates = [g for g in self.gate_ids if g not in _GATE_IDS]
        if not self.gate_ids or bad_gates:
            raise ValueError(f"Invalid gate_ids: {self.gate_ids!r}")
        for tid in self.task_ids:
            if tid not in _TASK_IDS:
                raise ValueError(f"Unknown task_ids entry: {tid!r}")
        if len(self.retest_date) != 10 or self.retest_date[4] != "-" or self.retest_date[7] != "-":
            raise ValueError("retest_date must be YYYY-MM-DD")
        for label, value in (
            ("os_name", self.os_name),
            ("os_version", self.os_version),
            ("browser_name", self.browser_name),
            ("browser_version", self.browser_version),
            ("at_name", self.at_name),
            ("at_version", self.at_version),
        ):
            if not value.strip():
                raise ValueError(f"HumanAtRecord requires {label}")
        return self

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HumanAtRecord:
        os_raw = data.get("os")
        browser_raw = data.get("browser")
        at_raw = data.get("at")
        os_info: dict[str, Any] = os_raw if isinstance(os_raw, dict) else {}
        browser: dict[str, Any] = browser_raw if isinstance(browser_raw, dict) else {}
        at: dict[str, Any] = at_raw if isinstance(at_raw, dict) else {}
        gate_raw = data.get("gate_ids") or ()
        task_ids_raw = data.get("task_ids") or ()
        if not isinstance(gate_raw, (list, tuple)) or any(not isinstance(g, str) for g in gate_raw):
            raise ValueError("HumanAtRecord.gate_ids must be an array of strings")
        if not isinstance(task_ids_raw, (list, tuple)) or any(
            not isinstance(t, str) for t in task_ids_raw
        ):
            raise ValueError("HumanAtRecord.task_ids must be an array of strings")
        redacted = data.get("redacted", False)
        stretch = data.get("stretch", False)
        if not isinstance(redacted, bool):
            raise ValueError("HumanAtRecord.redacted must be a boolean")
        if not isinstance(stretch, bool):
            raise ValueError("HumanAtRecord.stretch must be a boolean")
        gate_ids = tuple(gate_raw)
        task_ids = tuple(task_ids_raw)
        at_settings_raw = at.get("settings")
        return cls(
            record_id=str(data.get("record_id") or ""),
            gate_ids=gate_ids,
            combo_id=str(data.get("combo_id") or ""),
            os_name=str(os_info.get("name") or ""),
            os_version=str(os_info.get("version") or ""),
            browser_name=str(browser.get("name") or ""),
            browser_version=str(browser.get("version") or ""),
            at_name=str(at.get("name") or ""),
            at_version=str(at.get("version") or ""),
            task_id=str(data.get("task_id") or ""),
            result=str(data.get("result") or ""),
            owner=str(data.get("owner") or ""),
            retest_date=str(data.get("retest_date") or ""),
            redacted=redacted,
            stretch=stretch,
            session_id=str(data["session_id"]) if data.get("session_id") is not None else None,
            participant_category=(
                str(data["participant_category"])
                if data.get("participant_category") is not None
                else None
            ),
            at_settings=str(at_settings_raw) if at_settings_raw is not None else None,
            task_ids=task_ids,
            severity=str(data.get("severity") or "none"),
            known_issue=str(data.get("known_issue") or ""),
            issue_url=str(data["issue_url"]) if data.get("issue_url") is not None else None,
            waiver_id=str(data["waiver_id"]) if data.get("waiver_id") is not None else None,
            notes=str(data.get("notes") or ""),
        ).validated()

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "record_id": self.record_id,
            "gate_ids": list(self.gate_ids),
            "combo_id": self.combo_id,
            "stretch": self.stretch,
            "os": {"name": self.os_name, "version": self.os_version},
            "browser": {"name": self.browser_name, "version": self.browser_version},
            "at": {"name": self.at_name, "version": self.at_version},
            "task_id": self.task_id,
            "result": self.result,
            "severity": self.severity,
            "known_issue": self.known_issue,
            "owner": self.owner,
            "retest_date": self.retest_date,
            "notes": self.notes,
            "redacted": True,
        }
        if self.at_settings is not None:
            payload["at"]["settings"] = self.at_settings
        if self.session_id is not None:
            payload["session_id"] = self.session_id
        if self.participant_category is not None:
            payload["participant_category"] = self.participant_category
        if self.task_ids:
            payload["task_ids"] = list(self.task_ids)
        if self.issue_url is not None:
            payload["issue_url"] = self.issue_url
        if self.waiver_id is not None:
            payload["waiver_id"] = self.waiver_id
        return payload


@dataclass
class EvidenceInventory:
    """Collect contract, automation, human AT, and waiver evidence for release governance."""

    profile_id: str = ACCESSIBILITY_PROFILE.profile_id
    contracts: list[str] = field(default_factory=list)
    automation_results: list[dict[str, Any]] = field(default_factory=list)
    human_at_results: list[HumanAtRecord] = field(default_factory=list)
    waivers: list[Waiver] = field(default_factory=list)
    known_limitations: list[str] = field(default_factory=list)
    third_party_boundaries: list[str] = field(default_factory=list)
    feedback_route: str | None = None
    generated_at: str = field(
        default_factory=lambda: datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    def add_waiver(self, waiver: Waiver, *, today: date | None = None) -> None:
        self.waivers.append(waiver.validated(today=today))

    def add_human_at(self, record: HumanAtRecord) -> None:
        self.human_at_results.append(record.validated())

    def as_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "contracts": list(self.contracts),
            "automation_results": list(self.automation_results),
            "human_at_results": [r.as_dict() for r in self.human_at_results],
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
