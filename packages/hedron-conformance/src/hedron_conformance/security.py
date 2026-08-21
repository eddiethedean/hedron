"""Portable security conformance profile (CONFORM-056 / #550)."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from hedron_core.request_budget import (
    RequestBudget,
    get_request_budget,
    reset_request_budget,
    set_request_budget,
)
from hedron_core.request_plane import bind_request_security, unbind_request_security
from hedron_core.security_context import get_security_context
from hedron_core.security_plane import CONFORMANCE_PROFILE_VERSION, SecurityPolicy

SECURITY_PROFILE_ID = "security-control-plane"
SECURITY_PROFILE_VERSION = CONFORMANCE_PROFILE_VERSION


@dataclass(frozen=True, slots=True)
class SecurityConformanceCase:
    id: str
    adapter: str
    invariant: str
    earliest_enforcement: str
    expect: str  # pass | fail_closed
    payload: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SecurityConformanceResult:
    case_id: str
    adapter: str
    ok: bool
    detail: str = ""


DEFAULT_CASES: tuple[SecurityConformanceCase, ...] = (
    SecurityConformanceCase(
        id="csrf_before_handler",
        adapter="fastapi",
        invariant="csrf_before_handler",
        earliest_enforcement="ASGI receive / route wrap",
        expect="pass",
    ),
    SecurityConformanceCase(
        id="csrf_before_handler",
        adapter="flask",
        invariant="csrf_before_handler",
        earliest_enforcement="WSGI before view",
        expect="pass",
    ),
    SecurityConformanceCase(
        id="csrf_before_handler",
        adapter="django",
        invariant="csrf_before_handler",
        earliest_enforcement="middleware before view",
        expect="pass",
    ),
    SecurityConformanceCase(
        id="context_isolation",
        adapter="fastapi",
        invariant="security_context_isolation",
        earliest_enforcement="request ContextVar",
        expect="pass",
    ),
    SecurityConformanceCase(
        id="context_isolation",
        adapter="flask",
        invariant="security_context_isolation",
        earliest_enforcement="request ContextVar",
        expect="pass",
    ),
    SecurityConformanceCase(
        id="context_isolation",
        adapter="django",
        invariant="security_context_isolation",
        earliest_enforcement="request ContextVar",
        expect="pass",
    ),
    SecurityConformanceCase(
        id="budget_before_body",
        adapter="fastapi",
        invariant="request_budget_before_body",
        earliest_enforcement="ASGI streaming",
        expect="pass",
    ),
    SecurityConformanceCase(
        id="budget_before_body",
        adapter="flask",
        invariant="request_budget_before_body",
        earliest_enforcement="WSGI environ; deployment body limit",
        expect="pass",
    ),
    SecurityConformanceCase(
        id="budget_before_body",
        adapter="django",
        invariant="request_budget_before_body",
        earliest_enforcement="middleware; deployment body limit",
        expect="pass",
    ),
)


HOST_DISPOSITIONS = {
    "posit": {
        "portable_floor": "supported",
        "streaming_body": "unsupported",
        "deployment_control": "Connect/Workbench body size limits",
    },
    "notebook": {
        "portable_floor": "degraded",
        "streaming_body": "unsupported",
        "deployment_control": "localhost preview token gate",
    },
}


def security_profile_manifest() -> dict[str, Any]:
    return {
        "id": SECURITY_PROFILE_ID,
        "version": SECURITY_PROFILE_VERSION,
        "policy_presets": ["development", "standard", "strict"],
        "composition": "SecurityPolicy",
        "cases": [
            {
                "id": case.id,
                "adapter": case.adapter,
                "invariant": case.invariant,
                "earliest_enforcement": case.earliest_enforcement,
                "expect": case.expect,
            }
            for case in DEFAULT_CASES
        ],
        "host_dispositions": HOST_DISPOSITIONS,
    }


def _probe_context_isolation() -> bool:
    policy = SecurityPolicy.from_name("standard")
    binding = bind_request_security(policy=policy, application_id="conform-a")
    try:
        first = get_security_context()
        if first is None or first.application_id != "conform-a":
            return False
        nested = bind_request_security(policy=policy, application_id="conform-b")
        try:
            second = get_security_context()
            if second is None or second.application_id != "conform-b":
                return False
        finally:
            unbind_request_security(nested)
        restored = get_security_context()
        return restored is not None and restored.application_id == "conform-a"
    finally:
        unbind_request_security(binding)


def _probe_budget_before_body() -> bool:
    policy = SecurityPolicy.from_name("standard")
    if policy.request_budget_limits is None:
        return False
    budget = RequestBudget(limits=policy.request_budget_limits)
    token = set_request_budget(budget)
    try:
        active = get_request_budget()
        if active is not budget:
            return False
        budget.charge("body_bytes", 1)
        return budget.used("body_bytes") == 1
    finally:
        budget.close()
        reset_request_budget(token)


def _adapter_wiring_present(adapter: str) -> bool:
    if adapter == "fastapi":
        from importlib import import_module

        mod = import_module("hedron.security.plane_middleware")
        return hasattr(mod, "SecurityPlaneMiddleware")
    if adapter == "flask":
        from importlib import import_module

        mod = import_module("hedron_flask.blueprint")
        source = Path(mod.__file__ or "").read_text(encoding="utf-8")
        return "bind_request_security" in source
    if adapter == "django":
        from importlib import import_module

        mod = import_module("hedron_django.middleware")
        source = Path(mod.__file__ or "").read_text(encoding="utf-8")
        return "bind_request_security" in source
    return False


def _default_evaluator(case: SecurityConformanceCase) -> SecurityConformanceResult:
    policy = SecurityPolicy.from_name("standard")
    ok = policy.csrf_enabled and policy.conformance_profile_version == SECURITY_PROFILE_VERSION
    detail = "csrf+profile"
    if case.invariant == "csrf_before_handler":
        ok = ok and _adapter_wiring_present(case.adapter)
        detail = "csrf+wiring"
    elif case.invariant == "security_context_isolation":
        ok = _probe_context_isolation() and _adapter_wiring_present(case.adapter)
        detail = "contextvar+wiring"
    elif case.invariant == "request_budget_before_body":
        ok = _probe_budget_before_body() and _adapter_wiring_present(case.adapter)
        detail = "budget+wiring"
    return SecurityConformanceResult(case_id=case.id, adapter=case.adapter, ok=ok, detail=detail)


def run_security_profile(
    *,
    adapters: tuple[str, ...] = ("fastapi", "flask", "django"),
    evaluator: Callable[[SecurityConformanceCase], SecurityConformanceResult] | None = None,
) -> list[SecurityConformanceResult]:
    active = evaluator or _default_evaluator
    results: list[SecurityConformanceResult] = []
    for case in DEFAULT_CASES:
        if case.adapter not in adapters:
            continue
        results.append(active(case))
    return results


def differential_summary(
    results: list[SecurityConformanceResult],
) -> dict[str, Any]:
    by_invariant: dict[str, dict[str, bool]] = {}
    for result in results:
        by_invariant.setdefault(result.case_id, {})[result.adapter] = result.ok
    return {
        "profile_version": SECURITY_PROFILE_VERSION,
        "results": [
            {"case_id": r.case_id, "adapter": r.adapter, "ok": r.ok, "detail": r.detail}
            for r in results
        ],
        "by_invariant": by_invariant,
        "all_passed": all(r.ok for r in results),
        "host_dispositions": HOST_DISPOSITIONS,
    }


def write_fixture(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(security_profile_manifest(), indent=2) + "\n", encoding="utf-8")
