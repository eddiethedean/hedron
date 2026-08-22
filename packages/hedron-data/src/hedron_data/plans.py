"""Explicit server transform plans for bounded data execution."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from hedron_core.diagnostics import error
from hedron_core.typing_aliases import JsonValue
from hedron_data.sources import DataQuery

__all__ = [
    "TransformPlan",
    "TransformStep",
    "apply_plan_in_memory",
    "plan_from_query",
]

_ALLOWED_OPS = frozenset({"filter", "sort", "project", "aggregate", "sample", "search", "offset"})


def _sort_key(value: JsonValue) -> tuple[int, str, float | str]:
    if value is None:
        return (0, "", "")
    if isinstance(value, bool):
        return (1, "bool", "1" if value else "0")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return (2, "number", float(value))
    if isinstance(value, str):
        return (3, "str", value)
    return (4, type(value).__name__, str(value))


def _enforce_budgets(rows: Sequence[Mapping[str, JsonValue]], plan: TransformPlan) -> None:
    if len(rows) > plan.max_rows:
        raise error(
            "HED-DATA-0051",
            title="Transform row budget exceeded",
            explanation=f"Transform produced {len(rows)} rows; max_rows is {plan.max_rows}.",
            remediation="Lower the input or raise the explicit transform row budget.",
        )
    encoded = json.dumps(rows, default=str, separators=(",", ":")).encode("utf-8")
    if len(encoded) > plan.max_bytes:
        raise error(
            "HED-DATA-0051",
            title="Transform byte budget exceeded",
            explanation=(
                f"Transform produced {len(encoded)} bytes; max_bytes is {plan.max_bytes}."
            ),
            remediation="Lower the input or raise the explicit transform byte budget.",
        )


@dataclass(frozen=True, slots=True)
class TransformStep:
    op: str
    field: str | None = None
    value: JsonValue = None
    direction: str | None = None
    agg: str | None = None

    def validated(self) -> TransformStep:
        if self.op not in _ALLOWED_OPS:
            raise ValueError(f"Unknown transform op {self.op!r}")
        if self.op == "sort" and self.direction not in (None, "asc", "desc"):
            raise ValueError(f"Invalid sort direction {self.direction!r}")
        if self.op in {"filter", "sort", "project", "aggregate"} and not self.field:
            raise ValueError(f"Transform op {self.op!r} requires field")
        return self


@dataclass(frozen=True, slots=True)
class TransformPlan:
    """Inspectable server transform plan with budgets and tenant context."""

    steps: tuple[TransformStep, ...] = ()
    max_rows: int = 10_000
    max_bytes: int = 1_000_000
    tenant_id: str | None = None
    cancel_token: str | None = None
    auth_context: Mapping[str, JsonValue] = field(default_factory=dict)

    def validated(self) -> TransformPlan:
        if self.max_rows < 1:
            raise ValueError("TransformPlan.max_rows must be >= 1")
        if self.max_bytes < 1:
            raise ValueError("TransformPlan.max_bytes must be >= 1")
        steps = tuple(step.validated() for step in self.steps)
        return TransformPlan(
            steps=steps,
            max_rows=self.max_rows,
            max_bytes=self.max_bytes,
            tenant_id=self.tenant_id,
            cancel_token=self.cancel_token,
            auth_context=dict(self.auth_context),
        )

    def to_diagnostics(self) -> dict[str, Any]:
        plan = self.validated()
        return {
            "steps": [
                {
                    "op": step.op,
                    "field": step.field,
                    "direction": step.direction,
                    "agg": step.agg,
                    "has_value": step.value is not None,
                }
                for step in plan.steps
            ],
            "max_rows": plan.max_rows,
            "max_bytes": plan.max_bytes,
            "tenant_id": plan.tenant_id,
            "cancel_token": plan.cancel_token,
            "auth_keys": sorted(plan.auth_context),
        }


def plan_from_query(query: DataQuery, *, max_rows: int = 10_000) -> TransformPlan:
    q = query.validated()
    steps: list[TransformStep] = []
    for name, direction in q.sort:
        steps.append(TransformStep(op="sort", field=name, direction=direction))
    for name, value in q.filters.items():
        steps.append(TransformStep(op="filter", field=name, value=value))
    if q.search:
        steps.append(TransformStep(op="search", value=q.search))
    if q.projection:
        for name in q.projection:
            steps.append(TransformStep(op="project", field=name))
    if q.offset:
        steps.append(TransformStep(op="offset", value=q.offset))
    steps.append(TransformStep(op="sample", value=q.limit))
    return TransformPlan(steps=tuple(steps), max_rows=max_rows).validated()


def apply_plan_in_memory(
    rows: Sequence[Mapping[str, JsonValue]],
    plan: TransformPlan,
) -> list[dict[str, JsonValue]]:
    plan = plan.validated()
    result: list[dict[str, JsonValue]] = [dict(row) for row in rows]
    project_fields: list[str] = []
    for step in plan.steps:
        if step.op == "filter" and step.field is not None:
            result = [row for row in result if row.get(step.field) == step.value]
        elif step.op == "search" and isinstance(step.value, str):
            needle = step.value.lower()
            result = [row for row in result if any(needle in str(v).lower() for v in row.values())]
        elif step.op == "sort" and step.field is not None:
            reverse = step.direction == "desc"
            field_name = step.field
            result = sorted(
                result,
                key=lambda r, f=field_name: _sort_key(r.get(f)),
                reverse=reverse,
            )
        elif step.op == "project" and step.field is not None:
            project_fields.append(step.field)
        elif step.op == "offset":
            start = int(step.value) if isinstance(step.value, (int, float, str)) else 0
            result = result[max(0, start) :]
        elif step.op == "sample":
            limit = int(step.value) if isinstance(step.value, (int, float, str)) else plan.max_rows
            result = result[: max(0, min(int(limit), plan.max_rows))]
        elif step.op == "aggregate" and step.field is not None:
            values = [
                row.get(step.field)
                for row in result
                if isinstance(row.get(step.field), (int, float))
            ]
            agg = step.agg or "sum"
            if agg == "sum":
                total: float = float(sum(float(v) for v in values))  # type: ignore[arg-type]
            elif agg == "count":
                total = float(len(values))
            elif agg == "avg":
                total = float(sum(float(v) for v in values) / len(values)) if values else 0.0  # type: ignore[arg-type]
            else:
                raise ValueError(f"Unsupported aggregate {agg!r}")
            result = [{step.field: total}]
        _enforce_budgets(result, plan)
    if project_fields:
        result = [{k: row.get(k) for k in project_fields} for row in result]
        _enforce_budgets(result, plan)
    _enforce_budgets(result, plan)
    return result
