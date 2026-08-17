"""Explorer/CLI inspection facts. Never executes untrusted map data."""

from __future__ import annotations

from typing import Any

from hedron_maps.spec import MapPlan

__all__ = ["plan_facts"]


def plan_facts(plan: MapPlan) -> dict[str, Any]:
    return {
        "schema_id": plan.schema_id,
        "source_kind": plan.source_kind,
        "preset_id": plan.preset_id,
        "origins": list(plan.origins),
        "resources": list(plan.resources),
        "attribution": list(plan.attribution),
        "csp": dict(plan.csp),
        "limits": dict(plan.limits),
        "warnings": list(plan.warnings),
        "events": list(plan.events),
        "failure_states": list(plan.failure_states),
        "fallback_class": (plan.fallback or {}).get("alternative_class"),
        "plan_fingerprint": plan.plan_fingerprint,
        "executes_untrusted_data": False,
    }
