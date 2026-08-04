"""Adapter-neutral interaction values and policies (framework-neutral)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from typing import Any, Literal

from hedron_core.component import Component, NodeLike
from hedron_core.htmx_contract import (
    APPROVED_RESPONSE_HEADERS,
    HtmxContext,
    approved_headers,
    safe_css_selector,
)

__all__ = [
    "CacheHint",
    "FragmentRegion",
    "FragmentRegionError",
    "HistoryMode",
    "HtmxRequestFacts",
    "InteractionPolicy",
    "InteractionResult",
    "OobUpdate",
    "StatusPolicy",
    "authorize_oob_update",
    "default_interaction_policy",
    "form_sync_attrs",
    "interaction_headers",
    "materialize_interaction_nodes",
    "merge_interaction_headers",
    "merge_route_regions",
    "oob_swap",
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
class HtmxRequestFacts:
    """Portable HTMX request facts without a raw framework request object."""

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
        if key == "Cache-Control" and result.cache in {"private", "no-store"}:
            continue
        # Typed interaction headers win for approved HX URL/selector fields.
        if key in APPROVED_RESPONSE_HEADERS and key in headers:
            continue
        headers[key] = value
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
        vary = {"HX-Request", "HX-History-Restore-Request"}
        policy = result.policy
        if policy and policy.vary_on_target:
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
    return headers


def interaction_trace(result: InteractionResult) -> dict[str, Any]:
    return {
        "status_code": result.status_code,
        "target": result.target or result.retarget,
        "swap": result.swap or result.reswap,
        "oob_count": len(result.oob),
        "history": result.history,
        "cache": result.cache,
        "region_id": result.region_id,
        "explanation": result.explanation,
    }


def authorize_oob_update(
    update: OobUpdate,
    *,
    regions: tuple[FragmentRegion, ...] = (),
) -> None:
    if regions and update.select is None and update.element_id is None:
        raise ValueError(
            "OOB updates require element_id or select when fragment regions are declared"
        )
    if update.select is not None:
        if not safe_css_selector(update.select):
            raise ValueError("Unsafe OOB select selector")
        if regions:
            resolve_fragment_region(
                InteractionPolicy(declared_regions=regions),
                update.select,
            )
            # With declared regions, select must resolve to a concrete #id so
            # materialize can bind the rendered OOB target to that id.
            if update.element_id is None and not update.select.startswith("#"):
                raise ValueError(
                    "OOB select without element_id must be a #id when fragment regions are declared"
                )
    if update.element_id is not None:
        if not update.element_id.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Unsafe OOB element id")
        if regions:
            resolve_fragment_region(
                InteractionPolicy(declared_regions=regions),
                f"#{update.element_id}",
            )
        if update.select is not None and update.select.startswith("#"):
            selected_id = update.select[1:]
            if selected_id != update.element_id:
                raise ValueError("OOB element_id must match authorized select #id")


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
    pol = policy or default_interaction_policy()
    attrs: dict[str, str] = {}
    if pol.hx_sync:
        attrs["hx-sync"] = pol.hx_sync
    if pol.indicator:
        attrs["hx-indicator"] = pol.indicator
    if pol.aria_busy:
        attrs["aria-busy"] = "true"
    return attrs


def oob_swap(element_id: str, content: NodeLike | Component[Any], *, swap: str = "true") -> Any:
    """Mark a node for HTMX out-of-band swap via hx-swap-oob (framework-neutral)."""
    if not element_id.replace("-", "").replace("_", "").isalnum():
        raise ValueError("Unsafe OOB element id")
    from hedron_core.html import html

    return html.div(content, id=element_id, **{"hx-swap-oob": swap})


def _bound_oob_element_id(
    update: OobUpdate,
    *,
    regions: tuple[FragmentRegion, ...],
) -> str | None:
    if update.element_id is not None:
        return update.element_id
    if regions and update.select and update.select.startswith("#"):
        return update.select[1:]
    return None


def materialize_interaction_nodes(result: InteractionResult) -> Any | None:
    """Authorize OOB updates and return a renderable node tree (or None)."""
    from hedron_core.builtins import Fragment

    regions = result.policy.declared_regions if result.policy is not None else ()
    if not result.oob:
        return result.content
    nodes: list[Any] = []
    if result.content is not None:
        nodes.append(result.content)
    for update in result.oob:
        authorize_oob_update(update, regions=regions)
        bound_id = _bound_oob_element_id(update, regions=regions)
        if bound_id is not None:
            # Always wrap to the authorized id so caller content cannot emit a
            # different hx-swap-oob target under declared regions.
            node: Any = oob_swap(bound_id, update.content, swap=update.swap)
        else:
            node = update.content
        nodes.append(node)
    if not nodes:
        return None
    if len(nodes) == 1:
        return nodes[0]
    return Fragment(*nodes)
