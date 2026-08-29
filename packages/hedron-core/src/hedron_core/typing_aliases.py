"""Shared typing aliases for JSON, HTML attributes, and fixed public dict shapes."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TypeAlias, TypedDict, TypeGuard, cast

from typing_extensions import NotRequired

from hedron_core.security import SafeUrl

__all__ = [
    "AssetEntryDict",
    "CacheTraceDict",
    "DiagnosticDict",
    "HtmlAttrMap",
    "HtmlAttrValue",
    "HxLocation",
    "HxTriggerPayload",
    "InteractionTrace",
    "is_object_list",
    "is_string_mapping",
    "JobStatusDict",
    "JsonObject",
    "JsonPrimitive",
    "JsonValue",
    "PluginMetaDict",
    "RenderTrace",
    "SourceSpanDict",
]

JsonPrimitive: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]


def is_string_mapping(value: object) -> TypeGuard[Mapping[str, object]]:
    """Return whether *value* is a mapping whose keys are all strings.

    The guard is intended for JSON, TOML, and plugin boundaries where static
    types cannot describe decoded input before its container is validated.
    """
    if not isinstance(value, Mapping):
        return False
    mapping = cast(Mapping[object, object], value)
    return all(isinstance(key, str) for key in mapping)


def is_object_list(value: object) -> TypeGuard[list[object]]:
    """Narrow a decoded value to a mutable list with unknown element values."""
    return isinstance(value, list)


HtmlAttrValue: TypeAlias = (
    str | bool | int | float | SafeUrl | None | dict[str, str | bool | int | float | None]
)
HtmlAttrMap: TypeAlias = dict[str, HtmlAttrValue]

HxTriggerPayload: TypeAlias = str | dict[str, JsonValue]


class HxLocation(TypedDict):
    path: str
    target: NotRequired[str]
    select: NotRequired[str]
    swap: NotRequired[str]
    values: NotRequired[dict[str, JsonValue]]


class RenderTrace(TypedDict):
    path: str
    node_count: int
    session_node_count: int
    render_ordinal: int
    locale: str
    theme: str | None


class InteractionTrace(TypedDict):
    status_code: int
    target: str | None
    swap: str | None
    oob_count: int
    history: str
    cache: str | None
    region_id: str | None
    explanation: str
    action_phase: NotRequired[str]
    operation_id: NotRequired[str]
    generation: NotRequired[int]
    action_trace: NotRequired[dict[str, object]]


class JobStatusDict(TypedDict):
    job_id: str
    state: str
    job_type: str
    tenant_id: str | None
    auth_subject: str | None
    result: object | None
    error: str | None
    retry_after: int
    created_at: float
    updated_at: float
    cancel_requested: bool
    payload: NotRequired[dict[str, JsonValue]]
    idempotency_key: NotRequired[str]
    idempotency_scope_key: NotRequired[str]


class PluginMetaDict(TypedDict):
    name: str
    version: str
    distribution: str
    hedron_version: str
    capabilities: dict[str, bool]
    depends_on: list[str]


class SourceSpanDict(TypedDict):
    path: str
    start_line: int
    start_column: int
    end_line: int
    end_column: int


class DiagnosticDict(TypedDict):
    code: str
    severity: str
    title: str
    explanation: str
    remediation: str
    owner: str | None
    component_id: str | None
    context: dict[str, object]
    docs_url: str | None
    span: NotRequired[SourceSpanDict]
    applicability: NotRequired[dict[str, str | None]]
    actions: NotRequired[list[dict[str, str]]]


class AssetEntryDict(TypedDict):
    logical_id: str
    kind: str
    path: str
    digest: str
    content_type: str
    attributes: dict[str, str]


class CacheTraceDict(TypedDict):
    kind: str
    key_fingerprint: str
    scope: str
    age_ms: float | None
    size: int | None
    tags: list[str]
    detail: str | None
