"""Tagged public-wire unions. CatalogEntry.kind stays view/command."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

from hedron_core.codes import HED_FP_0004
from hedron_core.diagnostics import error
from hedron_core.typing_aliases import JsonObject, JsonValue

__all__ = [
    "PUBLIC_WIRE_DISCRIMINATOR",
    "PUBLIC_WIRE_SYMBOLS",
    "TaggedWire",
    "unknown_kind",
    "warn_smart_union",
    "wire_envelope",
]

PUBLIC_WIRE_DISCRIMINATOR = "kind"

# Stage 1 exact inventory (families locked in fastapi-unions-openapi-049.toml).
PUBLIC_WIRE_SYMBOLS: dict[str, tuple[str, ...]] = {
    "outcome_map_results": ("OutcomeMap", "OutcomeCase"),
    "typed_updates": ("Patch", "PatchSet", "RefreshIntent"),
    "selected_event_envelopes": (
        "GridCellEvent",
        "GridEditEvent",
        "GridSelectionEvent",
        "GridViewportEvent",
        "GridDragEvent",
        "GridPaginationEvent",
        "ChannelMessage",
    ),
    "job_messages": ("JobStatus", "JobHandle", "JobState"),
    "mcp_envelopes": ("McpResource", "McpTool"),
    "remote_adapter_descriptors": ("GradioEndpoint", "GradioRemoteConfig"),
}

WireKind = Literal[
    "outcome",
    "patch",
    "patch-set",
    "refresh-intent",
    "grid-event",
    "channel-message",
    "job-status",
    "mcp-resource",
    "mcp-tool",
    "gradio-endpoint",
    "gradio-remote-config",
]


@dataclass(frozen=True, slots=True)
class TaggedWire:
    kind: str
    payload: Mapping[str, JsonValue]


def wire_envelope(kind: str, payload: Mapping[str, Any] | None = None) -> JsonObject:
    data = dict(payload or {})
    existing = data.get(PUBLIC_WIRE_DISCRIMINATOR)
    if existing not in {None, kind}:
        raise error(
            HED_FP_0004,
            title="Public-wire kind mismatch",
            explanation=f"Envelope kind {existing!r} disagrees with {kind!r}.",
            remediation="Use a single literal discriminator named 'kind'.",
        )
    out: JsonObject = {PUBLIC_WIRE_DISCRIMINATOR: kind}
    for key, value in data.items():
        if key == PUBLIC_WIRE_DISCRIMINATOR:
            continue
        out[str(key)] = value  # type: ignore[assignment]
    return out


def unknown_kind(kind: str, *, allowed: tuple[str, ...]) -> None:
    if kind not in allowed:
        raise error(
            HED_FP_0004,
            title="Unknown public-wire variant",
            explanation=f"kind={kind!r} is outside {allowed!r}.",
            remediation="Reject unknown variants; do not smart-union public wire schemas.",
        )


def warn_smart_union(*, include_in_schema: bool, has_kind: bool) -> str | None:
    """Untagged application models stay valid; public catalog/wire should be tagged."""
    if include_in_schema and not has_kind:
        return "public-catalog-smart-union"
    return None
