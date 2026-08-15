"""Governed feedback collection (never treated as ground truth)."""

from __future__ import annotations

import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Protocol

from hedron_core.codes import HED_FEEDBACK_0001
from hedron_core.diagnostics import error
from hedron_core.model_demo.actions import ModelDemoError
from hedron_core.typing_aliases import JsonValue


@dataclass(frozen=True, slots=True)
class FeedbackPolicy:
    """Mandatory collection notice, tenant, redaction, retention, and abuse controls."""

    collection_notice: str
    consent_required: bool = True
    tenant_id: str | None = None
    redaction_fields: tuple[str, ...] = ()
    retention_seconds: float = 86400.0 * 30
    allow_export: bool = False
    abuse_controls: bool = True
    authorization_required: bool = True
    treat_as_ground_truth: bool = False

    def validate(self) -> None:
        if self.treat_as_ground_truth:
            raise ModelDemoError(
                "Feedback must not be treated as ground truth",
                code=HED_FEEDBACK_0001,
                diagnostic=error(
                    HED_FEEDBACK_0001,
                    title="Feedback ground-truth forbidden",
                    explanation="PredictionFeedback cannot be labeled ground truth.",
                    remediation="Keep treat_as_ground_truth=False.",
                ),
            )
        if not self.collection_notice.strip():
            raise ModelDemoError(
                "Missing collection notice",
                code=HED_FEEDBACK_0001,
                diagnostic=error(
                    HED_FEEDBACK_0001,
                    title="Missing collection notice",
                    explanation="Consent/collection notice is mandatory.",
                    remediation="Provide an explicit collection_notice string.",
                ),
            )
        if self.consent_required and self.tenant_id is None:
            raise ModelDemoError(
                "Tenant scope required with consent",
                code=HED_FEEDBACK_0001,
                diagnostic=error(
                    HED_FEEDBACK_0001,
                    title="Missing tenant scope",
                    explanation="Consentful feedback requires tenant_id.",
                    remediation="Set tenant_id on FeedbackPolicy.",
                ),
            )


@dataclass(frozen=True, slots=True)
class FeedbackRecord:
    record_id: str
    rating: int | None = None
    label: str | None = None
    reason: str | None = None
    correction: str | None = None
    input_refs: tuple[str, ...] = ()
    output_refs: tuple[str, ...] = ()
    consented: bool = False
    tenant_id: str | None = None
    created_at: float = 0.0
    redacted: Mapping[str, JsonValue] = field(default_factory=dict)


class FeedbackSink(Protocol):
    def store(self, record: FeedbackRecord) -> None: ...

    def delete(self, record_id: str) -> bool: ...

    def export(self) -> Sequence[FeedbackRecord]: ...


@dataclass
class InMemoryFeedbackSink:
    """Default sink for tests; respects export policy at the PredictionFeedback layer."""

    _records: dict[str, FeedbackRecord] = field(default_factory=dict)

    def store(self, record: FeedbackRecord) -> None:
        self._records[record.record_id] = record

    def delete(self, record_id: str) -> bool:
        return self._records.pop(record_id, None) is not None

    def export(self) -> Sequence[FeedbackRecord]:
        return tuple(self._records.values())


@dataclass
class PredictionFeedback:
    """Explicit-consent feedback collector with pluggable sinks."""

    policy: FeedbackPolicy
    sink: FeedbackSink
    enabled: bool = False
    max_text_chars: int = 2000
    max_records: int = 10_000
    _seq: int = field(default=0, init=False)
    _submit_times: list[float] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.policy.validate()

    def enable(self, *, consented: bool) -> None:
        if self.policy.consent_required and not consented:
            raise ModelDemoError(
                "Cannot enable feedback without consent",
                code=HED_FEEDBACK_0001,
                diagnostic=error(
                    HED_FEEDBACK_0001,
                    title="Consent required",
                    explanation="Feedback is never silently enabled.",
                    remediation="Collect explicit consent before enable().",
                ),
            )
        self.enabled = True

    def _require_principal(self, principal: str | None) -> None:
        if self.policy.authorization_required and not principal:
            raise ModelDemoError(
                "Feedback operation requires an authorized principal",
                code=HED_FEEDBACK_0001,
                diagnostic=error(
                    HED_FEEDBACK_0001,
                    title="Authorization required",
                    explanation="FeedbackPolicy.authorization_required is True.",
                    remediation="Pass principal=... for submit/export/delete.",
                ),
            )

    def _purge_expired(self, *, now: float | None = None) -> None:
        clock = time.time() if now is None else now
        retention = self.policy.retention_seconds
        if retention < 0:
            return
        for record in list(self.sink.export()):
            if clock - record.created_at > retention:
                self.sink.delete(record.record_id)

    def _enforce_abuse(self, *, reason: str | None, correction: str | None) -> None:
        if not self.policy.abuse_controls:
            return
        for label, text in (("reason", reason), ("correction", correction)):
            if text is not None and len(text) > self.max_text_chars:
                raise ModelDemoError(
                    f"Feedback {label} exceeds max_text_chars={self.max_text_chars}",
                    code=HED_FEEDBACK_0001,
                )
        now = time.time()
        window = 60.0
        self._submit_times = [t for t in self._submit_times if now - t < window]
        if len(self._submit_times) >= 60:
            raise ModelDemoError(
                "Feedback submit rate limit exceeded",
                code=HED_FEEDBACK_0001,
            )
        active = len(self.sink.export())
        if active >= self.max_records:
            raise ModelDemoError(
                f"Feedback store full (max_records={self.max_records})",
                code=HED_FEEDBACK_0001,
            )

    def submit(
        self,
        *,
        rating: int | None = None,
        label: str | None = None,
        reason: str | None = None,
        correction: str | None = None,
        input_refs: Sequence[str] = (),
        output_refs: Sequence[str] = (),
        consented: bool = False,
        payload: Mapping[str, JsonValue] | None = None,
        principal: str | None = None,
        now: float | None = None,
    ) -> FeedbackRecord:
        if not self.enabled:
            raise ModelDemoError(
                "Feedback is disabled",
                code=HED_FEEDBACK_0001,
                diagnostic=error(
                    HED_FEEDBACK_0001,
                    title="Feedback disabled",
                    explanation="PredictionFeedback defaults to disabled.",
                    remediation="Call enable(consented=True) first.",
                ),
            )
        if self.policy.consent_required and not consented:
            raise ModelDemoError(
                "Submission requires consent",
                code=HED_FEEDBACK_0001,
            )
        self._require_principal(principal)
        self._purge_expired(now=now)
        self._enforce_abuse(reason=reason, correction=correction)
        self._seq += 1
        redacted: dict[str, JsonValue] = {}
        for key, value in dict(payload or {}).items():
            if key in self.policy.redaction_fields:
                redacted[key] = "[redacted]"
            else:
                redacted[key] = value
        record = FeedbackRecord(
            record_id=f"fb-{self._seq}",
            rating=rating,
            label=label,
            reason=reason,
            correction=correction,
            input_refs=tuple(input_refs),
            output_refs=tuple(output_refs),
            consented=consented,
            tenant_id=self.policy.tenant_id,
            created_at=time.time() if now is None else now,
            redacted=redacted,
        )
        self.sink.store(record)
        self._submit_times.append(time.time() if now is None else now)
        return record

    def delete(self, record_id: str, *, principal: str | None = None) -> bool:
        self._require_principal(principal)
        self._purge_expired()
        return self.sink.delete(record_id)

    def export(
        self, *, principal: str | None = None, now: float | None = None
    ) -> Sequence[FeedbackRecord]:
        if not self.policy.allow_export:
            raise ModelDemoError(
                "Export not permitted by policy",
                code=HED_FEEDBACK_0001,
            )
        self._require_principal(principal)
        self._purge_expired(now=now)
        return self.sink.export()
