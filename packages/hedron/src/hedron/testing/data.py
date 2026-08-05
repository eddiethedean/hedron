"""Contract fixtures for bounded data sources, grid deltas, and chart events."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from hedron_core.typing_aliases import JsonValue
from hedron_core.visualization import (
    ChartAnnotation,
    ChartEvent,
    validate_annotation,
    validate_chart_event,
)

__all__ = [
    "AdversarialCase",
    "assert_accessible_fallback",
    "assert_budget",
    "assert_stable_row_identity",
    "assert_stable_trace_identity",
    "chart_event_fixture",
    "data_changes_fixture",
    "data_query_fixture",
    "grid_event_fixture",
    "labeled_adversarial_cases",
    "transform_plan_fixture",
]


CaseKind = Literal["valid", "adversarial"]


@dataclass(frozen=True, slots=True)
class AdversarialCase:
    name: str
    kind: CaseKind
    payload: Mapping[str, Any]
    expected_error: str | None = None


def data_query_fixture(
    *,
    offset: int = 0,
    limit: int = 25,
    sort: tuple[tuple[str, str], ...] = (),
    filters: Mapping[str, JsonValue] | None = None,
    allowlisted_sort_fields: frozenset[str] | None = frozenset({"name", "value"}),
    allowlisted_filter_fields: frozenset[str] | None = frozenset({"name", "value"}),
) -> Any:
    from hedron_data.sources import DataQuery

    return DataQuery(
        offset=offset,
        limit=limit,
        sort=sort,
        filters=dict(filters or {}),
        allowlisted_sort_fields=allowlisted_sort_fields,
        allowlisted_filter_fields=allowlisted_filter_fields,
    ).validated()


def data_changes_fixture(
    *,
    row_key: str = "1",
    field: str = "value",
    value: JsonValue = 1,
    dataset_version: str | None = "v1",
) -> Any:
    from hedron_data.sources import CellUpdate, DataChanges

    return DataChanges(
        updates=(CellUpdate(row_key=row_key, field=field, value=value),),
        dataset_version=dataset_version,
    )


def transform_plan_fixture(*, field: str = "value", limit: int = 10) -> Any:
    from hedron_data.plans import TransformPlan, TransformStep

    return TransformPlan(
        steps=(
            TransformStep(op="filter", field=field, value=1),
            TransformStep(op="sort", field=field, direction="asc"),
            TransformStep(op="sample", value=limit),
        ),
        max_rows=limit,
        auth_context={"tenant": "demo"},
    ).validated()


def grid_event_fixture(
    *,
    kind: str = "edit",
    row_key: str = "row-1",
    field: str = "value",
) -> Any:
    from hedron_data.events import (
        GridEditEvent,
        GridPaginationEvent,
        GridSelectionEvent,
        validate_grid_event,
    )

    if kind == "selection":
        event = GridSelectionEvent(row_key=row_key, field=field, payload={"selected": True})
    elif kind == "pagination":
        event = GridPaginationEvent(payload={"offset": 0, "limit": 25})
    else:
        event = GridEditEvent(row_key=row_key, field=field, payload={"value": 1})
    return validate_grid_event(event)


def chart_event_fixture(
    *,
    kind: str = "click",
    trace_id: str = "trace-0",
    point_index: int | None = 0,
) -> ChartEvent:
    return validate_chart_event(
        ChartEvent(
            kind=kind,
            trace_id=trace_id,
            point_index=point_index,
            payload={"x": 1, "y": 2},
            accessible_fallback="Selected point 1,2",
            debounce_ms=50,
            coalesce_key=f"{kind}:{trace_id}",
        )
    )


def labeled_adversarial_cases() -> list[AdversarialCase]:
    return [
        AdversarialCase(
            name="oversize-page",
            kind="adversarial",
            payload={"limit": 10_000},
            expected_error="DataQuery",
        ),
        AdversarialCase(
            name="filter-injection",
            kind="adversarial",
            payload={"filters": {"__proto__": "x"}},
            expected_error="allowlisted",
        ),
        AdversarialCase(
            name="chart-event-oversize",
            kind="adversarial",
            payload={"payload": {"blob": "x" * 80_000}},
            expected_error="budget",
        ),
        AdversarialCase(
            name="annotation-html",
            kind="adversarial",
            payload={"html": "<script>"},
            expected_error="HTML",
        ),
        AdversarialCase(
            name="valid-query",
            kind="valid",
            payload={"limit": 10},
        ),
    ]


def assert_stable_row_identity(rows: Sequence[Mapping[str, Any]], *, key: str = "id") -> None:
    keys = [str(row.get(key)) for row in rows]
    assert all(keys), "row identity missing"
    assert len(keys) == len(set(keys)), "row identity not stable/unique"


def assert_stable_trace_identity(events: Sequence[ChartEvent]) -> None:
    assert all(event.trace_id for event in events)


def assert_budget(
    payload: Mapping[str, Any] | Sequence[Any] | str | bytes, *, max_bytes: int
) -> None:
    if isinstance(payload, (str, bytes)):
        size = len(payload.encode("utf-8") if isinstance(payload, str) else payload)
    else:
        size = len(json.dumps(payload, default=str).encode("utf-8"))
    assert size <= max_bytes, f"payload {size} exceeds budget {max_bytes}"


def assert_accessible_fallback(
    *,
    description: str | None = None,
    alt: str | None = None,
    waiver: str | None = None,
    tabular_fallback: Sequence[Mapping[str, Any]] | None = None,
) -> None:
    ok = description or alt or waiver or tabular_fallback
    assert ok, "accessible fallback metadata required"


def annotation_fixture() -> ChartAnnotation:
    return validate_annotation(
        ChartAnnotation(
            kind="point",
            label="Peak",
            payload={"x": 1, "y": 2},
            description="Peak point",
        )
    )
