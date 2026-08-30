"""Typed grid interaction events with authorization and payload bounds."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from dataclasses import field as dc_field
from typing import Any, Literal

from hedron_core.diagnostics import error
from hedron_core.typing_aliases import JsonValue

__all__ = [
    "GridCellEvent",
    "GridDragEvent",
    "GridEditEvent",
    "GridEvent",
    "GridPaginationEvent",
    "GridSelectionEvent",
    "GridViewportEvent",
    "authorized_grid_event",
    "validate_grid_event",
]

GridEventKind = Literal["cell", "edit", "selection", "viewport", "drag", "pagination"]


@dataclass(frozen=True, slots=True)
class GridCellEvent:
    kind: Literal["cell"] = "cell"
    row_key: str = ""
    field: str | None = None
    payload: Mapping[str, JsonValue] = dc_field(default_factory=lambda: dict[str, JsonValue]())
    auth_context: Mapping[str, JsonValue] = dc_field(default_factory=lambda: dict[str, JsonValue]())
    debounce_ms: int = 0
    coalesce_key: str | None = None


@dataclass(frozen=True, slots=True)
class GridEditEvent:
    kind: Literal["edit"] = "edit"
    row_key: str = ""
    field: str | None = None
    payload: Mapping[str, JsonValue] = dc_field(default_factory=lambda: dict[str, JsonValue]())
    auth_context: Mapping[str, JsonValue] = dc_field(default_factory=lambda: dict[str, JsonValue]())
    debounce_ms: int = 0
    coalesce_key: str | None = None


@dataclass(frozen=True, slots=True)
class GridSelectionEvent:
    kind: Literal["selection"] = "selection"
    row_key: str = ""
    field: str | None = None
    payload: Mapping[str, JsonValue] = dc_field(default_factory=lambda: dict[str, JsonValue]())
    auth_context: Mapping[str, JsonValue] = dc_field(default_factory=lambda: dict[str, JsonValue]())
    debounce_ms: int = 0
    coalesce_key: str | None = None


@dataclass(frozen=True, slots=True)
class GridViewportEvent:
    kind: Literal["viewport"] = "viewport"
    row_key: str = ""
    field: str | None = None
    payload: Mapping[str, JsonValue] = dc_field(default_factory=lambda: dict[str, JsonValue]())
    auth_context: Mapping[str, JsonValue] = dc_field(default_factory=lambda: dict[str, JsonValue]())
    debounce_ms: int = 0
    coalesce_key: str | None = None


@dataclass(frozen=True, slots=True)
class GridDragEvent:
    kind: Literal["drag"] = "drag"
    row_key: str = ""
    field: str | None = None
    payload: Mapping[str, JsonValue] = dc_field(default_factory=lambda: dict[str, JsonValue]())
    auth_context: Mapping[str, JsonValue] = dc_field(default_factory=lambda: dict[str, JsonValue]())
    debounce_ms: int = 0
    coalesce_key: str | None = None


@dataclass(frozen=True, slots=True)
class GridPaginationEvent:
    kind: Literal["pagination"] = "pagination"
    row_key: str = ""
    field: str | None = None
    payload: Mapping[str, JsonValue] = dc_field(default_factory=lambda: dict[str, JsonValue]())
    auth_context: Mapping[str, JsonValue] = dc_field(default_factory=lambda: dict[str, JsonValue]())
    debounce_ms: int = 0
    coalesce_key: str | None = None


GridEvent = (
    GridCellEvent
    | GridEditEvent
    | GridSelectionEvent
    | GridViewportEvent
    | GridDragEvent
    | GridPaginationEvent
)


def validate_grid_event(event: GridEvent, *, max_payload_bytes: int = 65_536) -> GridEvent:
    raw_max_payload_bytes: Any = max_payload_bytes
    if (
        isinstance(raw_max_payload_bytes, bool)
        or not isinstance(raw_max_payload_bytes, int)
        or raw_max_payload_bytes < 1
    ):
        raise ValueError("max_payload_bytes must be a positive integer")
    if not event.row_key and event.kind not in {"viewport", "pagination"}:
        raise error(
            "HED-DATA-0025",
            title="Grid event missing stable row identity",
            explanation=f"{event.kind} events require row_key except viewport/pagination.",
            remediation="Supply a stable row_key from the data source.",
        )
    if event.debounce_ms < 0:
        raise ValueError("debounce_ms must be >= 0")
    try:
        encoded = json.dumps(dict(event.payload), default=str, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("grid event payload must be finite JSON") from exc
    if len(encoded) > max_payload_bytes:
        raise error(
            "HED-DATA-0026",
            title="Grid event payload exceeds budget",
            explanation=f"Payload is {len(encoded)} bytes; max is {max_payload_bytes}.",
            remediation="Reduce payload or raise an explicit authenticated budget.",
        )
    return event


def authorized_grid_event(
    event: GridEvent,
    *,
    allowed_fields: frozenset[str] | None = None,
    can_edit: bool = False,
) -> GridEvent:
    event = validate_grid_event(event)
    if event.kind == "edit" and not can_edit:
        raise error(
            "HED-DATA-0027",
            title="Grid edit event forbidden",
            explanation="Caller is not authorized to edit.",
            remediation="Require authentication and editable policy before accepting edits.",
        )
    if event.field is not None and allowed_fields is not None and event.field not in allowed_fields:
        raise error(
            "HED-DATA-0027",
            title="Grid event field not allowlisted",
            explanation=f"Field {event.field!r} is not writable/visible for this actor.",
            remediation="Restrict events to allowlisted fields.",
        )
    return event
