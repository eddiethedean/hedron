"""Build and merge approved HTMX response headers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from hedron_core.htmx.attrs import HtmxAttrs
from hedron_core.htmx.authorize import authorize_location_selectors, authorize_response_selector
from hedron_core.htmx.policy import (
    EXTRA_HEADER_KWARGS,
    InteractionPolicy,
    InteractionResult,
    StatusPolicy,
    default_interaction_policy,
)
from hedron_core.htmx_contract import APPROVED_RESPONSE_HEADERS, approved_headers
from hedron_core.typing_aliases import InteractionTrace


def validated_extra_headers(extra: Mapping[str, str]) -> dict[str, str]:
    """Validate adapter/caller ``extra_headers`` against the approved HTMX allowlist."""
    return _validated_extra_headers(extra)


def _validated_extra_headers(extra: Mapping[str, str]) -> dict[str, str]:
    if not extra:
        return {}
    kwargs: dict[str, Any] = {}
    other: dict[str, str] = {}
    for key, value in extra.items():
        if key == "HX-Refresh":
            kwargs["refresh"] = str(value).lower() == "true"
            continue
        if key in EXTRA_HEADER_KWARGS:
            arg = EXTRA_HEADER_KWARGS[key]
            if arg in {"push_url", "replace_url"} and str(value).lower() in {"true", "false"}:
                kwargs[arg] = str(value).lower() == "true"
            else:
                kwargs[arg] = value
            continue
        if key == "Vary":
            other[key] = value
            continue
        if key == "Cache-Control":
            lowered = str(value).lower()
            # Never accept cache directives that publish fragments to shared caches.
            if "public" in lowered or "s-maxage" in lowered:
                raise ValueError(
                    "Cache-Control must not use public or s-maxage on InteractionResult headers"
                )
            other[key] = value
            continue
        if key == "Retry-After":
            text = str(value).strip()
            if not text.isdigit() or int(text) < 0:
                raise ValueError("Retry-After must be a non-negative integer seconds value")
            other[key] = text
            continue
        if key in APPROVED_RESPONSE_HEADERS:
            raise ValueError(f"Unsupported approved header mapping for {key}")
        raise ValueError(f"Unapproved response header: {key}")
    out = approved_headers(**kwargs) if kwargs else {}
    out.update(other)
    return out


def merge_interaction_headers(
    result: InteractionResult,
    extra_headers: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Build interaction headers and safely merge adapter extras."""
    headers = interaction_headers(result)
    if not extra_headers:
        return headers
    validated = _validated_extra_headers(extra_headers)
    for key, value in validated.items():
        if key == "Cache-Control" and result.cache in {"private", "no-store", "vary-htmx"}:
            continue
        # Typed interaction headers win for approved HX URL/selector fields.
        if key in APPROVED_RESPONSE_HEADERS and key in headers:
            continue
        headers[key] = value
    # Re-check after adapter extras: typed fields already won above, but extras
    # may introduce HX-Retarget / HX-Reselect / HX-Location selectors when typed
    # fields were absent.
    _authorize_outbound_selectors(result.policy, headers)
    return headers


def interaction_headers(result: InteractionResult) -> dict[str, str]:
    """Build approved response headers from a portable InteractionResult."""
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
        # Default fragment policy: never leave bodies publicly cacheable.
        headers["Cache-Control"] = "private, no-store"
    # Always emit HTMX Vary so shared caches cannot mix page/fragment bodies,
    # including when Cache-Control is private / no-store.
    if result.cache in {"private", "no-store", "vary-htmx", None}:
        vary = {"HX-Request", "HX-History-Restore-Request"}
        policy = result.policy
        multi_region = bool(policy and len(policy.declared_regions) > 1)
        if policy and (policy.vary_on_target or multi_region):
            vary.add("HX-Target")
        existing = headers.get("Vary", "")
        parts = {p.strip() for p in existing.split(",") if p.strip()}
        parts.update(vary)
        headers["Vary"] = ", ".join(sorted(parts))
    extras = _validated_extra_headers(result.headers)
    for key, value in extras.items():
        if key == "Cache-Control" and result.cache in {"private", "no-store", "vary-htmx"}:
            # Typed cache policy owns Cache-Control; extras cannot weaken it.
            continue
        headers[key] = value
    # Authorize outbound selectors after typed + extra headers merge so neither
    # InteractionResult fields nor headers={} can bypass region policy.
    _authorize_outbound_selectors(result.policy, headers)
    return headers


def _authorize_outbound_selectors(
    policy: InteractionPolicy | None,
    headers: Mapping[str, str],
) -> None:
    """Authorize HX-Retarget / HX-Reselect / HX-Location target+select fields."""
    authorize_response_selector(
        policy,
        headers.get("HX-Retarget"),
        header_name="HX-Retarget",
    )
    authorize_response_selector(
        policy,
        headers.get("HX-Reselect"),
        header_name="HX-Reselect",
    )
    authorize_location_selectors(policy, headers.get("HX-Location"))


def interaction_trace(result: InteractionResult) -> InteractionTrace:
    trace: InteractionTrace = {
        "status_code": result.status_code,
        "target": result.target or result.retarget,
        "swap": result.swap or result.reswap,
        "oob_count": len(result.oob),
        "history": result.history,
        "cache": result.cache,
        "region_id": result.region_id,
        "explanation": result.explanation,
    }
    if result.action_state is not None:
        trace["action_phase"] = result.action_state.phase.value
        if result.action_state.operation is not None:
            trace["operation_id"] = result.action_state.operation.operation_id
            trace["generation"] = result.action_state.operation.generation
    if result.action_trace is not None:
        trace["action_trace"] = result.action_trace.to_dict()
    return trace


_STATUS_DEFAULTS: dict[int, StatusPolicy] = {
    202: StatusPolicy(202, message="Accepted", swap="innerHTML"),
    204: StatusPolicy(204, no_swap=True, message="No content"),
    401: StatusPolicy(401, message="Authentication required", retarget="#hedron-auth"),
    403: StatusPolicy(403, message="Forbidden", retarget="#hedron-auth"),
    409: StatusPolicy(409, message="Conflict", reswap="outerHTML"),
    422: StatusPolicy(
        422, message="Validation failed", retarget="#hedron-errors", reswap="innerHTML"
    ),
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
    pol = policy or default_interaction_policy()
    typed = HtmxAttrs(sync=pol.hx_sync, indicator=pol.indicator).as_html_attrs()
    attrs = {name: str(value) for name, value in typed.items()}
    if pol.aria_busy:
        attrs["aria-busy"] = "true"
    return attrs
