"""Model demo composition, examples, and governed feedback (RFC-0045 / RFC-0046).

``InferenceInterface`` / ``ModelDemo`` build reviewable surfaces only from explicitly
registered typed actions or callable adapters. Feedback requires consent and is never
treated as ground truth.
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

from hedron_core.codes import HED_DEMO_0001, HED_DEMO_0002, HED_DEMO_0003, HED_FEEDBACK_0001
from hedron_core.diagnostics import HedronError, error
from hedron_core.typing_aliases import JsonValue

__all__ = [
    "CachedExampleResult",
    "ExampleItem",
    "ExampleSet",
    "FeedbackPolicy",
    "FeedbackRecord",
    "FeedbackSink",
    "InferenceInterface",
    "ModelDemo",
    "ModelDemoError",
    "PredictionFeedback",
    "RegisteredAction",
    "RegisteredCallableAdapter",
    "ActionRegistry",
]


class ModelDemoError(ValueError):
    """Fail-closed model-demo generation or feedback policy error."""

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        diagnostic: HedronError | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.diagnostic = diagnostic


@dataclass(frozen=True, slots=True)
class RegisteredAction:
    """Explicitly registered typed action available for demo composition."""

    action_id: str
    input_schema: Mapping[str, Any]
    output_schema: Mapping[str, Any]
    side_effects: tuple[str, ...] = ()
    authorization_required: bool = True
    resource_policy: str | None = None
    http_exposed: bool = False
    mcp_exposed: bool = False
    description: str = ""
    preprocessing_version: str = "1"
    code_version: str = "1"
    model_version: str = "1"
    handler: Callable[..., Any] | None = None


@dataclass(frozen=True, slots=True)
class RegisteredCallableAdapter:
    """Callable adapter with explicit schemas and policies (never auto-published)."""

    adapter_id: str
    callable_ref: Callable[..., Any]
    input_schema: Mapping[str, Any]
    output_schema: Mapping[str, Any]
    side_effects: tuple[str, ...] = ()
    authorization_required: bool = True
    resource_policy: str | None = None
    http_exposed: bool = False
    mcp_exposed: bool = False
    description: str = ""
    preprocessing_version: str = "1"
    code_version: str = "1"
    model_version: str = "1"


@dataclass
class ActionRegistry:
    """Explicit registry — demos fail closed without a matching entry."""

    _actions: dict[str, RegisteredAction] = field(default_factory=dict)
    _adapters: dict[str, RegisteredCallableAdapter] = field(default_factory=dict)

    def register_action(self, action: RegisteredAction) -> None:
        if action.action_id in self._actions:
            raise ModelDemoError(f"Action already registered: {action.action_id!r}")
        self._actions[action.action_id] = action

    def register_adapter(self, adapter: RegisteredCallableAdapter) -> None:
        if adapter.adapter_id in self._adapters:
            raise ModelDemoError(f"Adapter already registered: {adapter.adapter_id!r}")
        self._adapters[adapter.adapter_id] = adapter

    def get_action(self, action_id: str) -> RegisteredAction | None:
        return self._actions.get(action_id)

    def get_adapter(self, adapter_id: str) -> RegisteredCallableAdapter | None:
        return self._adapters.get(adapter_id)


@dataclass(frozen=True, slots=True)
class InferenceInterface:
    """Reviewable input/result surface derived from a registered action or adapter."""

    interface_id: str
    source_id: str
    source_kind: str  # "action" | "adapter"
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    description: str = ""
    live_mode: bool = False
    debounce_ms: int = 0
    allow_submit: bool = True
    allow_clear: bool = True
    allow_stop: bool = True
    component_overrides: Mapping[str, str] = field(default_factory=dict)
    input_schema: Mapping[str, Any] = field(default_factory=dict)
    output_schema: Mapping[str, Any] = field(default_factory=dict)
    http_exposed: bool = False
    mcp_exposed: bool = False
    resource_policy: str | None = None
    authorization_required: bool = True


@dataclass
class ModelDemo:
    """Composition layer that builds ``InferenceInterface`` only from the registry."""

    registry: ActionRegistry
    title: str = "Model demo"
    _interfaces: dict[str, InferenceInterface] = field(default_factory=dict, init=False)

    def build_from_action(
        self,
        action_id: str,
        *,
        interface_id: str | None = None,
        inputs: Sequence[str] | None = None,
        outputs: Sequence[str] | None = None,
        live_mode: bool = False,
        debounce_ms: int = 0,
        component_overrides: Mapping[str, str] | None = None,
    ) -> InferenceInterface:
        action = self.registry.get_action(action_id)
        if action is None:
            raise ModelDemoError(
                f"Unregistered action: {action_id!r}",
                code=HED_DEMO_0001,
                diagnostic=error(
                    HED_DEMO_0001,
                    title="Unregistered action",
                    explanation="InferenceInterface requires an explicitly registered action.",
                    remediation="Register the action before building a demo.",
                ),
            )
        return self._build(
            source_id=action.action_id,
            source_kind="action",
            interface_id=interface_id or f"demo-{action.action_id}",
            input_schema=action.input_schema,
            output_schema=action.output_schema,
            side_effects=action.side_effects,
            authorization_required=action.authorization_required,
            resource_policy=action.resource_policy,
            http_exposed=action.http_exposed,
            mcp_exposed=action.mcp_exposed,
            description=action.description,
            inputs=inputs,
            outputs=outputs,
            live_mode=live_mode,
            debounce_ms=debounce_ms,
            component_overrides=component_overrides,
        )

    def build_from_adapter(
        self,
        adapter_id: str,
        *,
        interface_id: str | None = None,
        inputs: Sequence[str] | None = None,
        outputs: Sequence[str] | None = None,
        live_mode: bool = False,
        debounce_ms: int = 0,
        component_overrides: Mapping[str, str] | None = None,
    ) -> InferenceInterface:
        adapter = self.registry.get_adapter(adapter_id)
        if adapter is None:
            raise ModelDemoError(
                f"Unregistered callable adapter: {adapter_id!r}",
                code=HED_DEMO_0001,
                diagnostic=error(
                    HED_DEMO_0001,
                    title="Unregistered callable",
                    explanation="Arbitrary callables cannot become demos without registration.",
                    remediation="Register a RegisteredCallableAdapter with explicit policies.",
                ),
            )
        return self._build(
            source_id=adapter.adapter_id,
            source_kind="adapter",
            interface_id=interface_id or f"demo-{adapter.adapter_id}",
            input_schema=adapter.input_schema,
            output_schema=adapter.output_schema,
            side_effects=adapter.side_effects,
            authorization_required=adapter.authorization_required,
            resource_policy=adapter.resource_policy,
            http_exposed=adapter.http_exposed,
            mcp_exposed=adapter.mcp_exposed,
            description=adapter.description,
            inputs=inputs,
            outputs=outputs,
            live_mode=live_mode,
            debounce_ms=debounce_ms,
            component_overrides=component_overrides,
        )

    def build_from_callable(self, fn: Callable[..., Any], **_: Any) -> InferenceInterface:
        """Fail closed — bare callables are never auto-published."""
        raise ModelDemoError(
            "Cannot build InferenceInterface from an unregistered callable",
            code=HED_DEMO_0001,
            diagnostic=error(
                HED_DEMO_0001,
                title="Unregistered callable",
                explanation="Passing a raw callable is rejected.",
                remediation="Use register_adapter with explicit schemas and policies.",
            ),
        )

    def get(self, interface_id: str) -> InferenceInterface | None:
        return self._interfaces.get(interface_id)

    def _build(
        self,
        *,
        source_id: str,
        source_kind: str,
        interface_id: str,
        input_schema: Mapping[str, Any],
        output_schema: Mapping[str, Any],
        side_effects: tuple[str, ...],
        authorization_required: bool,
        resource_policy: str | None,
        http_exposed: bool,
        mcp_exposed: bool,
        description: str,
        inputs: Sequence[str] | None,
        outputs: Sequence[str] | None,
        live_mode: bool,
        debounce_ms: int,
        component_overrides: Mapping[str, str] | None,
    ) -> InferenceInterface:
        if not input_schema or not output_schema:
            raise ModelDemoError(
                "Ambiguous or missing input/output schema",
                code=HED_DEMO_0002,
                diagnostic=error(
                    HED_DEMO_0002,
                    title="Ambiguous schema",
                    explanation="Both input_schema and output_schema must be non-empty.",
                    remediation="Declare typed schemas on the registered action/adapter.",
                ),
            )
        undeclared = [s for s in side_effects if not s.strip()]
        if undeclared or (side_effects and any(s == "undeclared" for s in side_effects)):
            raise ModelDemoError(
                "Undeclared side effects",
                code=HED_DEMO_0002,
                diagnostic=error(
                    HED_DEMO_0002,
                    title="Undeclared side effects",
                    explanation="Side effects must be named explicitly.",
                    remediation="List concrete side-effect identifiers or use an empty tuple.",
                ),
            )
        if authorization_required and not resource_policy:
            raise ModelDemoError(
                "Missing resource policy for authorized demo",
                code=HED_DEMO_0003,
                diagnostic=error(
                    HED_DEMO_0003,
                    title="Missing resource policy",
                    explanation="Authorized demos require an explicit resource_policy.",
                    remediation="Set resource_policy on the registered action/adapter.",
                ),
            )
        if live_mode and not resource_policy:
            raise ModelDemoError(
                "Live/debounced mode requires resource policy",
                code=HED_DEMO_0003,
                diagnostic=error(
                    HED_DEMO_0003,
                    title="Missing live resource policy",
                    explanation="Declared live mode needs rate/resource policy.",
                    remediation="Provide resource_policy before enabling live_mode.",
                ),
            )
        # Accidental exposure: MCP/HTTP flags are independent; both default false.
        # Building a demo never flips them on.
        resolved_inputs = tuple(inputs) if inputs is not None else tuple(input_schema.keys())
        resolved_outputs = tuple(outputs) if outputs is not None else tuple(output_schema.keys())
        iface = InferenceInterface(
            interface_id=interface_id,
            source_id=source_id,
            source_kind=source_kind,
            inputs=resolved_inputs,
            outputs=resolved_outputs,
            description=description,
            live_mode=live_mode,
            debounce_ms=debounce_ms,
            component_overrides=dict(component_overrides or {}),
            input_schema=dict(input_schema),
            output_schema=dict(output_schema),
            http_exposed=http_exposed,
            mcp_exposed=mcp_exposed,
            resource_policy=resource_policy,
            authorization_required=authorization_required,
        )
        self._interfaces[interface_id] = iface
        return iface


@dataclass(frozen=True, slots=True)
class ExampleItem:
    example_id: str
    label: str
    inputs: Mapping[str, JsonValue]
    provenance: str = ""
    partial: bool = False
    authorized_roles: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CachedExampleResult:
    cache_key: str
    example_id: str
    outputs: Mapping[str, JsonValue]
    generated_at: float
    cost_units: float = 0.0
    stale: bool = False
    retention_seconds: float | None = None


@dataclass
class ExampleSet:
    """Versioned sample inputs with provenance and inspectable cached results."""

    set_id: str
    action_id: str
    model_version: str = "1"
    schema_version: str = "1"
    code_version: str = "1"
    preprocessing_version: str = "1"
    page_size: int = 10
    _items: list[ExampleItem] = field(default_factory=list, init=False)
    _cache: dict[str, CachedExampleResult] = field(default_factory=dict, init=False)

    def add(self, item: ExampleItem) -> None:
        self._items.append(item)

    def cache_key_for(self, example_id: str) -> str:
        material = "|".join(
            [
                self.action_id,
                self.model_version,
                self.schema_version,
                self.code_version,
                self.preprocessing_version,
                example_id,
            ]
        )
        return hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]

    def store_result(
        self,
        example_id: str,
        outputs: Mapping[str, JsonValue],
        *,
        cost_units: float = 0.0,
        retention_seconds: float | None = 86400.0,
    ) -> CachedExampleResult:
        key = self.cache_key_for(example_id)
        result = CachedExampleResult(
            cache_key=key,
            example_id=example_id,
            outputs=dict(outputs),
            generated_at=time.time(),
            cost_units=cost_units,
            retention_seconds=retention_seconds,
        )
        self._cache[key] = result
        return result

    def get_cached(
        self, example_id: str, *, now: float | None = None
    ) -> CachedExampleResult | None:
        key = self.cache_key_for(example_id)
        result = self._cache.get(key)
        if result is None:
            return None
        clock = time.time() if now is None else now
        if result.retention_seconds is not None:
            age = clock - result.generated_at
            if age > result.retention_seconds:
                return CachedExampleResult(
                    cache_key=result.cache_key,
                    example_id=result.example_id,
                    outputs=result.outputs,
                    generated_at=result.generated_at,
                    cost_units=result.cost_units,
                    stale=True,
                    retention_seconds=result.retention_seconds,
                )
        return result

    def invalidate(self, *, reason: str = "version") -> int:
        count = len(self._cache)
        self._cache.clear()
        return count

    def page(
        self, *, offset: int = 0, limit: int | None = None, role: str | None = None
    ) -> list[ExampleItem]:
        size = self.page_size if limit is None else limit
        items = [
            item
            for item in self._items
            if not item.authorized_roles or (role is not None and role in item.authorized_roles)
        ]
        return items[offset : offset + size]

    @property
    def size(self) -> int:
        return len(self._items)


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
