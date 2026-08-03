"""Typed FastAPI/HTMX interaction envelope for phase 0.6."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

from starlette.requests import Request

from hedron.htmx import HtmxContext, approved_headers, htmx_context, is_htmx_request
from hedron_core.component import Component, NodeLike

__all__ = [
    "FragmentRegion",
    "HtmxRequest",
    "InteractionPolicy",
    "InteractionResult",
    "OobUpdate",
    "StatusPolicy",
    "default_interaction_policy",
    "htmx_request",
    "interaction_headers",
    "resolve_fragment_region",
    "status_policy_for",
]

CacheHint = Literal["private", "no-store", "vary-htmx"]
HistoryMode = Literal["push", "replace", "none"]


@dataclass(frozen=True, slots=True)
class FragmentRegion:
    """Authorized fragment region declared on a route."""

    id: str
    selector: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class OobUpdate:
    content: NodeLike | Component[Any]
    swap: str = "true"
    select: str | None = None


@dataclass(frozen=True, slots=True)
class InteractionPolicy:
    """Defaults for sync, indicators, CSRF, focus, and error retarget."""

    hx_sync: str | None = "drop"
    indicator: str | None = None
    aria_busy: bool = True
    embed_csrf: bool = True
    restore_focus: bool = True
    idempotent_get: bool = True
    error_retarget: str | None = None
    error_reswap: str | None = "innerHTML"
    vary_on_target: bool = False
    declared_regions: tuple[FragmentRegion, ...] = ()


@dataclass(frozen=True, slots=True)
class StatusPolicy:
    status_code: int
    swap: str | None = "innerHTML"
    retarget: str | None = None
    reswap: str | None = None
    no_swap: bool = False
    message: str = ""


@dataclass(frozen=True, slots=True)
class HtmxRequest:
    """Request-scoped HTMX context wrapper."""

    request: Request
    context: HtmxContext

    @property
    def is_htmx(self) -> bool:
        return self.context.is_htmx

    @property
    def target(self) -> str | None:
        return self.context.target

    @property
    def boosted(self) -> bool:
        return self.context.boosted

    @property
    def history_restore(self) -> bool:
        return self.context.history_restore


@dataclass(frozen=True, slots=True)
class InteractionResult:
    """Primary content plus validated HTMX mechanics (headers stay inspectable)."""

    content: NodeLike | Component[Any] | None = None
    status_code: int = 200
    target: str | None = None
    swap: str | None = None
    oob: tuple[OobUpdate, ...] = ()
    trigger: str | Mapping[str, Any] | None = None
    trigger_after_swap: str | Mapping[str, Any] | None = None
    trigger_after_settle: str | Mapping[str, Any] | None = None
    push_url: str | bool | None = None
    replace_url: str | bool | None = None
    refresh: bool = False
    retarget: str | None = None
    reswap: str | None = None
    reselect: str | None = None
    location: str | Mapping[str, Any] | None = None
    history: HistoryMode = "none"
    cache: CacheHint | None = "vary-htmx"
    concurrency: str | None = None
    region_id: str | None = None
    policy: InteractionPolicy | None = None
    headers: Mapping[str, str] = field(default_factory=dict)
    explanation: str = ""


def default_interaction_policy(**overrides: Any) -> InteractionPolicy:
    base = InteractionPolicy()
    if not overrides:
        return base
    data = {**base.__dict__, **overrides}
    return InteractionPolicy(**data)


def htmx_request(request: Request) -> HtmxRequest:
    return HtmxRequest(request=request, context=htmx_context(request))


def resolve_fragment_region(
    policy: InteractionPolicy | None,
    target: str | None,
) -> FragmentRegion | None:
    if policy is None or not policy.declared_regions:
        return None
    if target is None:
        return policy.declared_regions[0] if policy.declared_regions else None
    for region in policy.declared_regions:
        if region.selector == target or region.id == target or target.lstrip("#") == region.id:
            return region
    raise ValueError(f"HX-Target {target!r} is not an authorized fragment region for this route")


def interaction_headers(
    result: InteractionResult,
    *,
    request: Request | None = None,
) -> dict[str, str]:
    headers = approved_headers(
        trigger=result.trigger,
        trigger_after_swap=result.trigger_after_swap,
        trigger_after_settle=result.trigger_after_settle,
        push_url=result.push_url,
        replace_url=result.replace_url,
        refresh=result.refresh,
        retarget=result.retarget or result.target,
        reswap=result.reswap or result.swap,
        reselect=result.reselect,
        location=result.location,
    )
    if result.history == "push" and "HX-Push-Url" not in headers:
        headers["HX-Push-Url"] = "true"
    elif result.history == "replace" and "HX-Replace-Url" not in headers:
        headers["HX-Replace-Url"] = "true"
    if result.cache == "vary-htmx":
        vary = {"HX-Request", "HX-History-Restore-Request"}
        policy = result.policy
        if policy and policy.vary_on_target:
            vary.add("HX-Target")
        existing = headers.get("Vary", "")
        parts = {p.strip() for p in existing.split(",") if p.strip()}
        parts.update(vary)
        headers["Vary"] = ", ".join(sorted(parts))
    headers.update(dict(result.headers))
    if request is not None and is_htmx_request(request):
        # Keep mechanics visible for Explorer traces.
        request.state.hedron_interaction = {
            "status_code": result.status_code,
            "target": result.target or result.retarget,
            "swap": result.swap or result.reswap,
            "oob_count": len(result.oob),
            "history": result.history,
            "cache": result.cache,
            "region_id": result.region_id,
            "explanation": result.explanation,
        }
    return headers


_STATUS_DEFAULTS: dict[int, StatusPolicy] = {
    202: StatusPolicy(202, message="Accepted", swap="innerHTML"),
    204: StatusPolicy(204, no_swap=True, message="No content"),
    401: StatusPolicy(401, message="Authentication required", retarget="#hedron-auth"),
    403: StatusPolicy(403, message="Forbidden", retarget="#hedron-auth"),
    409: StatusPolicy(409, message="Conflict", reswap="outerHTML"),
    422: StatusPolicy(422, message="Validation failed", reswap="innerHTML"),
    429: StatusPolicy(429, message="Too many requests", reswap="innerHTML"),
    500: StatusPolicy(500, message="Server error", retarget="#hedron-errors"),
}


def status_policy_for(status_code: int) -> StatusPolicy:
    if status_code in _STATUS_DEFAULTS:
        return _STATUS_DEFAULTS[status_code]
    if status_code >= 500:
        return _STATUS_DEFAULTS[500]
    return StatusPolicy(status_code)


def form_sync_attrs(policy: InteractionPolicy | None = None) -> dict[str, str]:
    """Attribute defaults for synchronized accessible forms/search."""
    pol = policy or default_interaction_policy()
    attrs: dict[str, str] = {}
    if pol.hx_sync:
        attrs["hx-sync"] = pol.hx_sync
    if pol.indicator:
        attrs["hx-indicator"] = pol.indicator
    if pol.aria_busy:
        attrs["aria-busy"] = "true"
    return attrs
