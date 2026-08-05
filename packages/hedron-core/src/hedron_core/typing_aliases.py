"""Shared typing aliases for JSON, HTML attributes, and fixed public dict shapes."""

from __future__ import annotations

from typing import NotRequired, TypeAlias, TypedDict

from hedron_core.security import SafeUrl

__all__ = [
    "HtmlAttrValue",
    "HxLocation",
    "HxTriggerPayload",
    "InteractionTrace",
    "JobStatusDict",
    "JsonPrimitive",
    "JsonValue",
    "PluginMetaDict",
    "RenderTrace",
]

JsonPrimitive: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]

HtmlAttrValue: TypeAlias = (
    str | bool | int | float | SafeUrl | None | dict[str, str | bool | int | float | None]
)

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
