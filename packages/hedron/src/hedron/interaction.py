"""Typed FastAPI/HTMX interaction envelope for phase 0.6."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from typing import Any, Literal

from starlette.requests import Request

from hedron.htmx import (
    APPROVED_RESPONSE_HEADERS,
    HtmxContext,
    _safe_css_selector,
    approved_headers,
    htmx_context,
    is_htmx_request,
)
from hedron_core.component import Component, NodeLike

__all__ = [
    "FragmentRegion",
    "FragmentRegionError",
    "HtmxRequest",
    "InteractionPolicy",
    "InteractionResult",
    "OobUpdate",
    "StatusPolicy",
    "default_interaction_policy",
    "htmx_request",
    "interaction_headers",
    "merge_route_regions",
    "resolve_fragment_region",
    "status_policy_for",
]

CacheHint = Literal["private", "no-store", "vary-htmx"]
HistoryMode = Literal["push", "replace", "none"]

_EXTRA_HEADER_KWARGS: dict[str, str] = {
    "HX-Redirect": "redirect",
    "HX-Push-Url": "push_url",
    "HX-Replace-Url": "replace_url",
    "HX-Retarget": "retarget",
    "HX-Reswap": "reswap",
    "HX-Reselect": "reselect",
    "HX-Location": "location",
    "HX-Trigger": "trigger",
    "HX-Trigger-After-Swap": "trigger_after_swap",
    "HX-Trigger-After-Settle": "trigger_after_settle",
}


class FragmentRegionError(ValueError):
    """HX-Target is not an authorized declared fragment region."""


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
    element_id: str | None = None


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
    redirect: str | None = None
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


def merge_route_regions(
    result: InteractionResult,
    route_regions: tuple[FragmentRegion, ...],
) -> InteractionResult:
    """Route-declared regions are authoritative when present."""
    if not route_regions:
        return result
    policy = result.policy or InteractionPolicy()
    return replace(result, policy=replace(policy, declared_regions=route_regions))


def resolve_fragment_region(
    policy: InteractionPolicy | None,
    target: str | None,
) -> FragmentRegion | None:
    if policy is None or not policy.declared_regions:
        return None
    if target is None:
        return policy.declared_regions[0] if policy.declared_regions else None
    needle = target.lstrip("#")
    for region in policy.declared_regions:
        if (
            region.selector == target
            or region.id == target
            or region.selector == f"#{needle}"
            or region.id == needle
        ):
            return region
    raise FragmentRegionError(
        f"HX-Target {target!r} is not an authorized fragment region for this route"
    )


def _validated_extra_headers(extra: Mapping[str, str]) -> dict[str, str]:
    """Re-validate InteractionResult.headers through approved_headers / allowlist."""
    if not extra:
        return {}
    kwargs: dict[str, Any] = {}
    other: dict[str, str] = {}
    for key, value in extra.items():
        if key == "HX-Refresh":
            kwargs["refresh"] = str(value).lower() == "true"
            continue
        if key in _EXTRA_HEADER_KWARGS:
            arg = _EXTRA_HEADER_KWARGS[key]
            if arg in {"push_url", "replace_url"} and str(value).lower() in {"true", "false"}:
                kwargs[arg] = str(value).lower() == "true"
            else:
                kwargs[arg] = value
            continue
        if key in {"Cache-Control", "Vary"}:
            other[key] = value
            continue
        if key in APPROVED_RESPONSE_HEADERS:
            raise ValueError(f"Unsupported approved header mapping for {key}")
        raise ValueError(f"Unapproved response header: {key}")
    out = approved_headers(**kwargs) if kwargs else {}
    out.update(other)
    return out


def interaction_headers(
    result: InteractionResult,
    *,
    request: Request | None = None,
) -> dict[str, str]:
    headers = approved_headers(
        trigger=result.trigger,
        trigger_after_swap=result.trigger_after_swap,
        trigger_after_settle=result.trigger_after_settle,
        redirect=result.redirect,
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
    if result.cache == "private":
        headers["Cache-Control"] = "private"
    elif result.cache == "no-store":
        headers["Cache-Control"] = "private, no-store"
    elif result.cache == "vary-htmx":
        vary = {"HX-Request", "HX-History-Restore-Request"}
        policy = result.policy
        if policy and policy.vary_on_target:
            vary.add("HX-Target")
        existing = headers.get("Vary", "")
        parts = {p.strip() for p in existing.split(",") if p.strip()}
        parts.update(vary)
        headers["Vary"] = ", ".join(sorted(parts))
    # Validated extras may add headers but cannot skip local-URL / selector checks.
    extras = _validated_extra_headers(result.headers)
    for key, value in extras.items():
        if key == "Cache-Control" and result.cache in {"private", "no-store"}:
            # Typed cache hints win over raw Cache-Control overrides.
            continue
        headers[key] = value
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


def authorize_oob_update(
    update: OobUpdate,
    *,
    regions: tuple[FragmentRegion, ...] = (),
) -> None:
    """Validate OOB swap/select against CSS safety and optional region allowlist.

    When ``regions`` is non-empty, OOB ``select`` / ``element_id`` must name an
    authorized region (declare OOB destinations alongside primary targets).
    """
    if update.select is not None:
        if not _safe_css_selector(update.select):
            raise ValueError("Unsafe OOB select selector")
        if regions:
            resolve_fragment_region(
                InteractionPolicy(declared_regions=regions),
                update.select,
            )
    if update.element_id is not None:
        if not update.element_id.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Unsafe OOB element id")
        if regions:
            resolve_fragment_region(
                InteractionPolicy(declared_regions=regions),
                f"#{update.element_id}",
            )


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
