"""Portable type-driven authoring markers and TypeSchema (phase 0.44)."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Literal, cast

from hedron_core.codes import HED_TYPE_0004, HED_TYPE_0010
from hedron_core.diagnostics import error
from hedron_core.typing_aliases import JsonObject, JsonValue
from hedron_core.updates import BaseHandleDescriptor, descriptor_fingerprint

TYPE_SCHEMA_NAMESPACE = "hedron.type"
TYPE_SCHEMA_VERSION = 1
MAX_MODEL_FIELDS = 256
MAX_SCHEMA_DEPTH = 16
MAX_UNION_VARIANTS = 32
MAX_VALIDATION_ERRORS = 100

EffectKnowledge = Literal["dynamic", "declared"]
HandlerKind = Literal["view", "command"]
ControlDisposition = Literal["supported", "override_only", "rejected"]

__all__ = [
    "ControlDisposition",
    "EffectKnowledge",
    "HandlerKind",
    "InstanceKey",
    "MAX_MODEL_FIELDS",
    "MAX_SCHEMA_DEPTH",
    "MAX_UNION_VARIANTS",
    "MAX_VALIDATION_ERRORS",
    "Sensitive",
    "TYPE_SCHEMA_NAMESPACE",
    "TYPE_SCHEMA_VERSION",
    "TypeSchema",
    "attach_type_schema",
    "redact_type_payload",
    "stable_fingerprint",
]


@dataclass(frozen=True, slots=True)
class Sensitive:
    """Request framework-owned redaction for a model field or boundary."""

    redact_as: str = "[redacted]"

    def __post_init__(self) -> None:
        token = str(self.redact_as)
        if "<" in token or ">" in token or "\x00" in token:
            raise error(
                HED_TYPE_0010,
                title="Unsafe Sensitive replacement text",
                explanation="redact_as must be bounded plain text without HTML.",
                remediation="Use a short placeholder such as '[redacted]'.",
            )


@dataclass(frozen=True, slots=True)
class InstanceKey:
    """Include a validated field in non-reversible bound-instance identity."""

    include: bool = True


def stable_fingerprint(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:32]


def redact_type_payload(payload: Mapping[str, JsonValue]) -> JsonObject:
    """Copy a TypeSchema mapping, never copying values/defaults/examples/callbacks."""
    forbidden = {"values", "defaults", "examples", "callbacks", "request", "model"}
    out: JsonObject = {}
    for key, value in payload.items():
        if key in forbidden:
            continue
        out[str(key)] = value
    return out


@dataclass(frozen=True, slots=True)
class TypeSchema:
    """Versioned redacted extension attached under ``hedron.type``."""

    schema_version: int = TYPE_SCHEMA_VERSION
    handler_fingerprint: str = ""
    model_fingerprint: str = ""
    descriptor_fingerprint: str = ""
    handler_kind: HandlerKind = "view"
    boundary_sources: tuple[str, ...] = ()
    field_paths: tuple[Mapping[str, JsonValue], ...] = ()
    control_dispositions: Mapping[str, str] = field(default_factory=dict)
    sensitivity_flags: tuple[str, ...] = ()
    identity_flags: tuple[str, ...] = ()
    effect_knowledge: EffectKnowledge = "dynamic"
    declared_target_ids: tuple[str, ...] = ()
    outcome_variant_ids: tuple[str, ...] = ()
    fallback_cache_projection: Mapping[str, JsonValue] = field(default_factory=dict)
    diagnostics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.schema_version != TYPE_SCHEMA_VERSION:
            raise error(
                HED_TYPE_0004,
                title="Unsupported TypeSchema version",
                explanation=f"schema_version={self.schema_version} is not supported.",
                remediation=f"Use TypeSchema version {TYPE_SCHEMA_VERSION}.",
            )
        if len(self.field_paths) > MAX_MODEL_FIELDS:
            raise error(
                HED_TYPE_0004,
                title="TypeSchema field limit exceeded",
                explanation=f"Model has {len(self.field_paths)} fields; max is {MAX_MODEL_FIELDS}.",
                remediation="Split the boundary model.",
            )
        object.__setattr__(self, "control_dispositions", dict(self.control_dispositions))
        object.__setattr__(self, "fallback_cache_projection", dict(self.fallback_cache_projection))

    def as_mapping(self) -> JsonObject:
        payload: JsonObject = {
            "schema_version": self.schema_version,
            "handler_fingerprint": self.handler_fingerprint,
            "model_fingerprint": self.model_fingerprint,
            "descriptor_fingerprint": self.descriptor_fingerprint,
            "handler_kind": self.handler_kind,
            "boundary_sources": list(self.boundary_sources),
            "field_paths": [dict(item) for item in self.field_paths],
            "control_dispositions": dict(self.control_dispositions),
            "sensitivity_flags": list(self.sensitivity_flags),
            "identity_flags": list(self.identity_flags),
            "effect_knowledge": self.effect_knowledge,
            "declared_target_ids": list(self.declared_target_ids),
            "outcome_variant_ids": list(self.outcome_variant_ids),
            "fallback_cache_projection": dict(self.fallback_cache_projection),
            "diagnostics": list(self.diagnostics),
        }
        return redact_type_payload(payload)


def attach_type_schema(
    descriptor: BaseHandleDescriptor,
    schema: TypeSchema,
) -> BaseHandleDescriptor:
    """Return a copy of ``descriptor`` with a redacted ``hedron.type`` extension."""
    payload = schema.as_mapping()
    if schema.descriptor_fingerprint and (
        schema.descriptor_fingerprint != descriptor_fingerprint(descriptor)
    ):
        raise error(
            HED_TYPE_0004,
            title="TypeSchema fingerprint mismatch",
            explanation="hedron.type metadata does not match the 0.43 descriptor fingerprint.",
            remediation="Rebuild the TypeSchema from the live handle descriptor.",
        )
    extensions = dict(descriptor.extensions)
    extensions[TYPE_SCHEMA_NAMESPACE] = payload
    from dataclasses import replace

    linked = TypeSchema(
        schema_version=schema.schema_version,
        handler_fingerprint=schema.handler_fingerprint,
        model_fingerprint=schema.model_fingerprint,
        descriptor_fingerprint=descriptor_fingerprint(descriptor),
        handler_kind=schema.handler_kind,
        boundary_sources=schema.boundary_sources,
        field_paths=schema.field_paths,
        control_dispositions=schema.control_dispositions,
        sensitivity_flags=schema.sensitivity_flags,
        identity_flags=schema.identity_flags,
        effect_knowledge=schema.effect_knowledge,
        declared_target_ids=schema.declared_target_ids,
        outcome_variant_ids=schema.outcome_variant_ids,
        fallback_cache_projection=schema.fallback_cache_projection,
        diagnostics=schema.diagnostics,
    )
    payload = linked.as_mapping()
    extensions[TYPE_SCHEMA_NAMESPACE] = payload
    return replace(
        descriptor,
        effect=linked.effect_knowledge,
        extensions=extensions,
    )


def _json_int(value: object, default: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        return default
    return value


def _json_str_tuple(value: object) -> tuple[str, ...]:
    if isinstance(value, str) or not isinstance(value, Sequence):
        return ()
    return tuple(str(item) for item in value)


def _json_str_map(value: object) -> dict[str, str]:
    if not isinstance(value, Mapping):
        return {}
    return {str(key): str(item) for key, item in value.items()}


def _json_object(value: object) -> JsonObject:
    if not isinstance(value, Mapping):
        return {}
    return {str(key): cast("JsonValue", item) for key, item in value.items()}


def type_schema_from_descriptor(descriptor: BaseHandleDescriptor) -> TypeSchema | None:
    payload = descriptor.extensions.get(TYPE_SCHEMA_NAMESPACE)
    if not isinstance(payload, Mapping):
        return None
    raw_paths = payload.get("field_paths")
    paths: Sequence[object] = (
        raw_paths
        if isinstance(raw_paths, Sequence) and not isinstance(raw_paths, (str, bytes))
        else ()
    )
    return TypeSchema(
        schema_version=_json_int(payload.get("schema_version"), TYPE_SCHEMA_VERSION),
        handler_fingerprint=str(payload.get("handler_fingerprint") or ""),
        model_fingerprint=str(payload.get("model_fingerprint") or ""),
        descriptor_fingerprint=str(payload.get("descriptor_fingerprint") or ""),
        handler_kind="command" if payload.get("handler_kind") == "command" else "view",
        boundary_sources=_json_str_tuple(payload.get("boundary_sources")),
        field_paths=tuple(item for item in paths if isinstance(item, Mapping)),
        control_dispositions=_json_str_map(payload.get("control_dispositions")),
        sensitivity_flags=_json_str_tuple(payload.get("sensitivity_flags")),
        identity_flags=_json_str_tuple(payload.get("identity_flags")),
        effect_knowledge=(
            "declared" if payload.get("effect_knowledge") == "declared" else "dynamic"
        ),
        declared_target_ids=_json_str_tuple(payload.get("declared_target_ids")),
        outcome_variant_ids=_json_str_tuple(payload.get("outcome_variant_ids")),
        fallback_cache_projection=_json_object(payload.get("fallback_cache_projection")),
        diagnostics=_json_str_tuple(payload.get("diagnostics")),
    )
