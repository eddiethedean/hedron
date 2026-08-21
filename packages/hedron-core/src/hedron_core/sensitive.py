"""Provenance-aware sensitive-data labels (SENS-056)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Generic, TypeVar

from hedron_core.security.secrets import Secret, is_secret, redact_value

T = TypeVar("T")


class SensitivityClass(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    CREDENTIAL = "credential"


class SensitiveSinkError(ValueError):
    """Raised when labeled sensitive data reaches an unauthorized sink."""


@dataclass(frozen=True, slots=True)
class SensitiveLabel:
    """Authoritative sensitivity provenance for a value."""

    classification: SensitivityClass
    source: str
    path: str = ""
    reason: str = ""

    def allows_sink(self, sink: str, *, allow: frozenset[SensitivityClass] | None = None) -> bool:
        permitted = allow or frozenset({SensitivityClass.PUBLIC, SensitivityClass.INTERNAL})
        return self.classification in permitted


@dataclass(frozen=True, slots=True)
class SensitiveValue(Generic[T]):
    """Value wrapped with an authoritative sensitivity label."""

    value: T
    label: SensitiveLabel

    def reveal(self) -> T:
        return self.value

    def redacted(self) -> str:
        return redact_value(self.value)


@dataclass(frozen=True, slots=True)
class DeclassificationRecord:
    source_label: SensitiveLabel
    target_classification: SensitivityClass
    reason: str
    actor: str = ""
    audited: bool = True


_DEFAULT_SINK_ALLOW: dict[str, frozenset[SensitivityClass]] = {
    "log": frozenset(set(SensitivityClass)),
    "audit": frozenset(set(SensitivityClass)),
    "html": frozenset({SensitivityClass.PUBLIC}),
    "export": frozenset({SensitivityClass.PUBLIC}),
    "telemetry": frozenset(set(SensitivityClass)),
    "cache_key": frozenset({SensitivityClass.PUBLIC, SensitivityClass.INTERNAL}),
    "validation_error": frozenset(set(SensitivityClass)),
    "trusted_sink": frozenset(set(SensitivityClass)),
}

_DECLASSIFICATION_LOG: list[DeclassificationRecord] = []


def label_for(value: Any, *, source: str = "inferred", path: str = "") -> SensitiveLabel | None:
    """Derive a label from Secret wrappers or return None for unlabeled values."""
    if isinstance(value, SensitiveValue):
        return value.label
    if is_secret(value) or isinstance(value, Secret):
        return SensitiveLabel(
            classification=SensitivityClass.SECRET,
            source=source,
            path=path,
        )
    return None


def enforce_sink(
    value: Any,
    *,
    sink: str,
    path: str = "",
    allow: frozenset[SensitivityClass] | None = None,
) -> Any:
    """Reject or redact labeled sensitive values at framework-owned sinks."""
    if isinstance(value, SensitiveValue):
        permitted = allow or _DEFAULT_SINK_ALLOW.get(sink, frozenset({SensitivityClass.PUBLIC}))
        if not value.label.allows_sink(sink, allow=permitted):
            raise SensitiveSinkError(
                f"sensitive value denied at sink {sink!r} "
                f"(class={value.label.classification.value})"
            )
        if value.label.classification in {
            SensitivityClass.SECRET,
            SensitivityClass.CREDENTIAL,
            SensitivityClass.CONFIDENTIAL,
        } and sink in {"log", "audit", "telemetry", "validation_error", "export"}:
            redacted = value.redacted()
            if str(value.reveal()) and str(value.reveal()) in str(redacted):
                return "[redacted]"
            return redacted
        return value.reveal()
    label = label_for(value, path=path)
    if label is None:
        return value
    return enforce_sink(SensitiveValue(value, label), sink=sink, path=path, allow=allow)


def declassify(
    value: SensitiveValue[T],
    *,
    target: SensitivityClass,
    reason: str,
    actor: str = "",
) -> SensitiveValue[T]:
    """Explicit policy-authorized declassification with audit record."""
    if not reason.strip():
        raise SensitiveSinkError("declassification requires a non-empty reason")
    record = DeclassificationRecord(
        source_label=value.label,
        target_classification=target,
        reason=reason,
        actor=actor,
    )
    _DECLASSIFICATION_LOG.append(record)
    return SensitiveValue(
        value.value,
        SensitiveLabel(
            classification=target,
            source=f"declassified:{value.label.source}",
            path=value.label.path,
            reason=reason,
        ),
    )


def declassification_records() -> tuple[DeclassificationRecord, ...]:
    return tuple(_DECLASSIFICATION_LOG)


def clear_declassification_records() -> None:
    _DECLASSIFICATION_LOG.clear()


def walk_and_enforce(obj: Any, *, sink: str, path: str = "") -> Any:
    """Recursively enforce sink policy on nested containers."""
    if isinstance(obj, SensitiveValue) or is_secret(obj) or isinstance(obj, Secret):
        return enforce_sink(obj, sink=sink, path=path)
    if isinstance(obj, dict):
        return {
            key: walk_and_enforce(val, sink=sink, path=f"{path}.{key}" if path else str(key))
            for key, val in obj.items()
        }
    if isinstance(obj, list):
        return [
            walk_and_enforce(item, sink=sink, path=f"{path}[{idx}]") for idx, item in enumerate(obj)
        ]
    if isinstance(obj, tuple):
        return tuple(
            walk_and_enforce(item, sink=sink, path=f"{path}[{idx}]") for idx, item in enumerate(obj)
        )
    return obj
