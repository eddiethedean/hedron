"""Workbench-flow testing helpers for phase 0.16."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

__all__ = [
    "SandboxBudgetFixture",
    "assert_action_authorized",
    "assert_http_fallback_present",
    "assert_transform_plan_bounded",
    "image_region_fixture",
    "json_document_fixture",
    "sandbox_budget_fixture",
    "tree_document_fixture",
    "workbench_action_fixture",
]


@dataclass(frozen=True, slots=True)
class SandboxBudgetFixture:
    cpu_ms: int = 5_000
    memory_mb: int = 256
    output_chars: int = 100_000
    packages: tuple[str, ...] = ()


def tree_document_fixture(
    *,
    nodes: Sequence[Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Deterministic tree document for TreeView / workbench scenarios."""
    if nodes is not None:
        return [dict(n) for n in nodes]
    return [
        {
            "id": "root",
            "label": "Root",
            "children": [
                {"id": "a", "label": "Alpha", "children": []},
                {
                    "id": "b",
                    "label": "Beta",
                    "children": [{"id": "b1", "label": "Beta-1", "children": []}],
                },
            ],
        }
    ]


def json_document_fixture(
    *,
    payload: Mapping[str, Any] | None = None,
    schema: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    doc = dict(payload or {"name": "demo", "count": 1})
    # Ensure serializable — fixtures never eval code.
    json.dumps(doc)
    result: dict[str, Any] = {"document": doc}
    if schema is not None:
        json.dumps(schema)
        result["schema"] = dict(schema)
    return result


def image_region_fixture(
    *,
    kind: str = "box",
    points: Sequence[Sequence[float]] | None = None,
) -> dict[str, Any]:
    pts = [list(p) for p in (points or ((0.1, 0.1), (0.5, 0.5)))]
    for pt in pts:
        if len(pt) != 2 or any(c < 0.0 or c > 1.0 for c in pt):
            raise ValueError("image_region_fixture points must be normalized")
    return {"kind": kind, "points": pts}


def sandbox_budget_fixture(
    *,
    cpu_ms: int = 5_000,
    memory_mb: int = 256,
    output_chars: int = 100_000,
    packages: Sequence[str] = (),
) -> SandboxBudgetFixture:
    return SandboxBudgetFixture(
        cpu_ms=cpu_ms,
        memory_mb=memory_mb,
        output_chars=output_chars,
        packages=tuple(packages),
    )


def workbench_action_fixture(
    *,
    action: str = "export",
    authorized: bool = True,
    payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "action": action,
        "authorized": authorized,
        "payload": dict(payload or {}),
    }


def assert_transform_plan_bounded(plan: Any, *, max_rows: int) -> None:
    """Assert a TransformPlan (or plan-like mapping) respects row bounds."""
    if hasattr(plan, "max_rows"):
        rows = int(plan.max_rows)
    elif isinstance(plan, Mapping):
        rows = int(plan.get("max_rows", -1))
    else:
        raise AssertionError(f"Not a transform plan: {type(plan)!r}")
    if rows < 1 or rows > max_rows:
        raise AssertionError(f"Transform plan max_rows={rows} exceeds bound {max_rows}")


def assert_action_authorized(action: Mapping[str, Any], *, expect: bool = True) -> None:
    """Assert a *fixture* action mapping's ``authorized`` boolean.

    This helper only checks the synthetic ``workbench_action_fixture`` field. It is
    not application authorization evidence — use real HTTP/authz tests for that.
    """
    authorized = action.get("authorized")
    if not isinstance(authorized, bool):
        raise AssertionError("Fixture authorized field must be a boolean")
    if authorized != expect:
        raise AssertionError(f"Expected authorized={expect}, got {authorized}")


def assert_http_fallback_present(html: str, *, token: str) -> None:
    if token not in html:
        raise AssertionError(f"Expected HTTP/static fallback token {token!r} in markup")
