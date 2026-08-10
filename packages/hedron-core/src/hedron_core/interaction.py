"""Adapter-neutral interaction values and policies (framework-neutral)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace
from typing import Any, Literal

from hedron_core.component import NodeLike
from hedron_core.htmx_contract import (
    APPROVED_RESPONSE_HEADERS,
    HtmxContext,
    approved_headers,
    safe_css_selector,
)
from hedron_core.typing_aliases import HxLocation, InteractionTrace, JsonValue

__all__ = [
    "CacheHint",
    "FragmentRegion",
    "FragmentRegionError",
    "HistoryMode",
    "HtmxRequestFacts",
    "InteractionPolicy",
    "InteractionResult",
    "OOB_ENVELOPE_TAGS",
    "OobEnvelopeTag",
    "OobUpdate",
    "RESERVED_OOB_ELEMENT_IDS",
    "StatusPolicy",
    "authorize_htmx_target",
    "authorize_oob_update",
    "apply_allow_undeclared_targets",
    "conflicting_select_oob_targets",
    "default_interaction_policy",
    "form_sync_attrs",
    "interaction_headers",
    "materialize_interaction_nodes",
    "merge_interaction_headers",
    "merge_route_regions",
    "oob_swap",
    "oob_update_element_ids",
    "parse_select_oob_element_ids",
    "resolve_fragment_region",
    "select_htmx_auth_target",
    "status_policy_for",
    "unparsed_select_oob_tokens",
    "validated_extra_headers",
]

CacheHint = Literal["private", "no-store", "vary-htmx"]
HistoryMode = Literal["push", "replace", "none"]
OobEnvelopeTag = Literal["div", "section", "aside", "main", "nav"]
OOB_ENVELOPE_TAGS: frozenset[str] = frozenset({"div", "section", "aside", "main", "nav"})

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

    def __init__(
        self,
        message: str,
        *,
        requested: str | None = None,
        declared: tuple[str, ...] = (),
        code: str | None = None,
    ) -> None:
        super().__init__(message)
        from hedron_core.codes import HED_HTMX_0001

        self.requested = requested
        self.declared = declared
        self.code = code or HED_HTMX_0001


@dataclass(frozen=True, slots=True)
class FragmentRegion:
    """Authorized fragment region declared on a route."""

    id: str
    selector: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class OobUpdate:
    """Out-of-band fragment update.

    Prefer one OOB mechanism per target: either request-side ``hx-select-oob``
    *or* a server ``OobUpdate`` with ``hx-swap-oob``. Combining both for the same
    id can replace a semantic host (for example ``<nav aria-label=...>``) with
    Hedron's OOB envelope. Use :func:`conflicting_select_oob_targets` /
    ``hedron check`` to detect that conflict.

    Default ``swap`` is ``innerHTML`` so landmark hosts keep their tag and
    accessible name. ``tag`` is defense in depth when an envelope must match a
    landmark host; it does not replace avoiding the ``select_oob`` + ``OobUpdate``
    conflict.
    """

    content: NodeLike
    swap: str = "innerHTML"
    select: str | None = None
    element_id: str | None = None
    tag: OobEnvelopeTag = "div"

    def __post_init__(self) -> None:
        if self.tag not in OOB_ENVELOPE_TAGS:
            raise ValueError(
                f"Unsupported OobUpdate tag={self.tag!r}; allowlisted: {sorted(OOB_ENVELOPE_TAGS)}"
            )


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
    # When False (default), HTMX HX-Target without declared regions is rejected.
    allow_undeclared_targets: bool = False


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
    """Primary content plus validated HTMX mechanics (headers stay inspectable).

    Prefer returning ``InteractionResult`` (or helpers such as ``swap(...)``) from
    fragment and action handlers when you need explicit HTMX headers.

    Args:
        content: Node tree rendered for the response body (may be ``None`` for
            header-only redirects / refreshes).
        status_code: HTTP status for the response.
        target: Optional ``HX-Retarget`` selector override.
        swap: Optional ``HX-Reswap`` strategy override.
        oob: Out-of-band updates applied alongside the primary swap.
        trigger: ``HX-Trigger`` event name or JSON-compatible mapping.
        trigger_after_swap: ``HX-Trigger-After-Swap`` payload.
        trigger_after_settle: ``HX-Trigger-After-Settle`` payload.
        push_url: ``HX-Push-Url`` value (``True`` uses the request URL).
        replace_url: ``HX-Replace-Url`` value.
        redirect: ``HX-Redirect`` or location redirect target when policy allows.
        refresh: When ``True``, emit ``HX-Refresh``.
        retarget: Alternate spelling forwarded as retarget header when set.
        reswap: Alternate spelling forwarded as reswap header when set.
        reselect: ``HX-Reselect`` selector.
        location: ``HX-Location`` payload.
        history: History mode for the interaction (``none`` by default).
        cache: Cache hint for response headers (``vary-htmx`` by default).
        concurrency: Optional concurrency token / key for adaptive controls.
        region_id: Declared fragment region id this result targets.
        policy: Interaction policy including declared regions and OOB rules.
        headers: Extra response headers (must pass HTMX allowlist validation).
        explanation: Optional human-readable note for diagnostics / Explorer.

    Raises:
        FragmentRegionError: When resolving a request target that is not an
            authorized declared region (via ``resolve_fragment_region`` helpers).

    Examples:
        >>> from hedron_core.interaction import InteractionResult
        >>> InteractionResult(content=None, status_code=200, refresh=True)
        InteractionResult(...)
    """

    content: NodeLike | None = None
    status_code: int = 200
    target: str | None = None
    swap: str | None = None
    oob: tuple[OobUpdate, ...] = ()
    trigger: str | Mapping[str, JsonValue] | None = None
    trigger_after_swap: str | Mapping[str, JsonValue] | None = None
    trigger_after_settle: str | Mapping[str, JsonValue] | None = None
    push_url: str | bool | None = None
    replace_url: str | bool | None = None
    redirect: str | None = None
    refresh: bool = False
    retarget: str | None = None
    reswap: str | None = None
    reselect: str | None = None
    location: str | HxLocation | Mapping[str, JsonValue] | None = None
    history: HistoryMode = "none"
    cache: CacheHint | None = "vary-htmx"
    concurrency: str | None = None
    region_id: str | None = None
    policy: InteractionPolicy | None = None
    headers: Mapping[str, str] = field(default_factory=dict)
    explanation: str = ""

    def __post_init__(self) -> None:
        code = self.status_code
        # Reject bool (subclass of int) and non-int; coerce int-like strings.
        if type(code) is bool:
            raise TypeError("status_code must be int, not bool")
        if type(code) is not int:
            try:
                code = int(code)  # type: ignore[arg-type]
            except (TypeError, ValueError) as exc:
                raise TypeError(
                    f"status_code must be int, got {type(self.status_code).__name__}"
                ) from exc
            object.__setattr__(self, "status_code", code)
        if self.oob:
            bad = [item for item in self.oob if not isinstance(item, OobUpdate)]
            if bad:
                raise TypeError(
                    "InteractionResult.oob items must be OobUpdate instances; "
                    f"got {[type(item).__name__ for item in bad]}"
                )


def default_interaction_policy(**overrides: Any) -> InteractionPolicy:
    base = InteractionPolicy()
    if not overrides:
        return base
    data = {**base.__dict__, **overrides}
    return InteractionPolicy(**data)


def apply_allow_undeclared_targets(
    result: InteractionResult,
    allow: bool,
) -> InteractionResult:
    """Merge route-level ``allow_undeclared_targets`` into the result policy."""
    if not allow:
        return result
    policy = result.policy or InteractionPolicy()
    if policy.allow_undeclared_targets:
        return result
    return replace(result, policy=replace(policy, allow_undeclared_targets=True))


def merge_route_regions(
    result: InteractionResult,
    route_regions: tuple[FragmentRegion, ...],
) -> InteractionResult:
    """Route-declared regions are authoritative when present."""
    if not route_regions:
        return result
    policy = result.policy or InteractionPolicy()
    return replace(result, policy=replace(policy, declared_regions=route_regions))


def _declared_region_labels(regions: tuple[FragmentRegion, ...]) -> tuple[str, ...]:
    return tuple(f"{region.id} ({region.selector})" for region in regions)


def _single_hash_id(value: str) -> str | None:
    """Return the id after at most one leading ``#``, or None if malformed.

    Rejects ``##panel`` / ``###panel`` (``str.lstrip('#')`` would collapse them).
    """
    if value.startswith("##"):
        return None
    return value.removeprefix("#")


def resolve_fragment_region(
    policy: InteractionPolicy | None,
    target: str | None,
) -> FragmentRegion | None:
    """Resolve ``target`` against declared regions by ``selector`` match.

    Authorization is selector-based (``FragmentRegion.id`` is bookkeeping only).
    Accepts either the exact declared selector (``#panel``) or HTMX's common bare-id
    header form (``panel``) when the selector is a single ``#id``. Rejects
    ``##…`` collapsing and matching on ``region.id`` when it differs from the
    selector id.
    """
    if policy is None or not policy.declared_regions:
        return None
    if target is None:
        return policy.declared_regions[0] if policy.declared_regions else None
    if target.startswith("##"):
        declared = _declared_region_labels(policy.declared_regions)
        raise FragmentRegionError(
            f"HX-Target {target!r} is not an authorized fragment region for this route",
            requested=target,
            declared=declared,
        )
    for region in policy.declared_regions:
        if region.selector == target:
            return region
        # HTMX frequently sends HX-Target without the leading '#' for #id selectors.
        if (
            region.selector.startswith("#")
            and not region.selector.startswith("##")
            and "#" not in region.selector[1:]
            and target == region.selector[1:]
        ):
            return region
    declared = _declared_region_labels(policy.declared_regions)
    raise FragmentRegionError(
        f"HX-Target {target!r} is not an authorized fragment region for this route",
        requested=target,
        declared=declared,
    )


def select_htmx_auth_target(
    *,
    client_target: str | None,
    region_id: str | None,
) -> str | None:
    """Choose the HTMX target used for authorization.

    Prefer the client ``HX-Target`` when present. When both client target and
    handler ``region_id`` are set but refer to different ids, reject — the
    browser swaps into ``HX-Target``, so authorizing ``region_id`` alone is
    fail-open. ``region_id`` is compared with a single leading ``#`` stripped
    (never ``lstrip``), and multi-hash targets are rejected.
    """
    if client_target and client_target.startswith("##"):
        raise FragmentRegionError(
            f"HX-Target {client_target!r} is not a valid fragment selector",
            requested=client_target,
            declared=(region_id,) if region_id else (),
        )
    if client_target and region_id:
        client_id = _single_hash_id(client_target)
        handler_id = _single_hash_id(region_id)
        if client_id is None or handler_id is None or client_id != handler_id:
            raise FragmentRegionError(
                f"HX-Target {client_target!r} disagrees with region_id {region_id!r}",
                requested=client_target,
                declared=(region_id,),
            )
        return client_target
    if client_target:
        return client_target
    if region_id is None:
        return None
    # Server bookkeeping ids are not CSS selectors; normalize to #id so
    # resolve_fragment_region can exact-match the common selector=f"#{id}" form
    # without accepting bare client HX-Target values.
    if region_id.startswith("##"):
        raise FragmentRegionError(
            f"region_id {region_id!r} is not a valid fragment selector",
            requested=region_id,
            declared=(region_id,),
        )
    return region_id if region_id.startswith("#") else f"#{region_id}"


def authorize_htmx_target(
    policy: InteractionPolicy | None,
    target: str | None,
    *,
    is_htmx: bool,
    history_restore: bool = False,
) -> FragmentRegion | None:
    """Authorize ``HX-Target`` for HTMX requests (fail closed by default).

    When the client sends ``HX-Target`` and no ``declared_regions`` are present,
    raise :class:`FragmentRegionError` unless ``allow_undeclared_targets`` is set.
    HTMX fragment requests with declared regions but a missing ``HX-Target`` also fail
    closed (do not implicitly authorize the first region). History-restore requests
    may omit ``HX-Target`` and still succeed (full PAGE navigation restore).
    """
    regions = policy.declared_regions if policy is not None else ()
    allow_open = bool(policy is not None and policy.allow_undeclared_targets)
    if is_htmx and target and not regions and not allow_open:
        raise FragmentRegionError(
            "HX-Target requires declared fragment_regions on this route "
            "(set InteractionPolicy.allow_undeclared_targets=True to opt out)",
            requested=target,
            declared=(),
        )
    if is_htmx and regions and not target and not allow_open and not history_restore:
        raise FragmentRegionError(
            "HTMX requests with declared fragment_regions require HX-Target",
            requested=None,
            declared=_declared_region_labels(regions),
        )
    if not regions or target is None:
        return None
    return resolve_fragment_region(policy, target)


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
    return headers


def interaction_trace(result: InteractionResult) -> InteractionTrace:
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


# Framework-owned OOB sinks that swap(toast=...) may target without declaring them on
# every fragment route. Does not weaken HX-Target authorization for primary swaps.
RESERVED_OOB_ELEMENT_IDS = frozenset({"hedron-toast"})


def _is_reserved_oob_target(*, element_id: str | None, select: str | None) -> bool:
    if element_id is not None and element_id in RESERVED_OOB_ELEMENT_IDS:
        return True
    if select is not None:
        needle = _single_hash_id(select)
        if needle is not None and needle in RESERVED_OOB_ELEMENT_IDS and select == f"#{needle}":
            return True
    return False


def authorize_oob_update(
    update: OobUpdate,
    *,
    regions: tuple[FragmentRegion, ...] = (),
) -> None:
    if update.select is None and update.element_id is None:
        raise ValueError("OOB updates require element_id or select")
    reserved = _is_reserved_oob_target(element_id=update.element_id, select=update.select)
    # Fail closed: without declared regions, only reserved toast/chrome ids are allowed.
    if not regions and not reserved:
        raise ValueError(
            "OOB updates require declared fragment regions (or a reserved element id "
            f"such as {sorted(RESERVED_OOB_ELEMENT_IDS)})"
        )
    if update.select is not None:
        if not safe_css_selector(update.select):
            raise ValueError("Unsafe OOB select selector")
        if regions and not reserved:
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
        if regions and not reserved:
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


def parse_select_oob_element_ids(select_oob: str | None) -> frozenset[str]:
    """Extract simple ``#id`` targets from an ``hx-select-oob`` value.

    Only ``#id`` tokens (alphanumeric / ``_`` / ``-``) are recognized. Complex
    selectors are ignored for conflict detection; use
    :func:`unparsed_select_oob_tokens` to surface them.
    """
    if not select_oob:
        return frozenset()
    ids: set[str] = set()
    for part in select_oob.split(","):
        token = part.strip()
        if not token or not safe_css_selector(token) or not token.startswith("#"):
            continue
        element_id = token[1:]
        if element_id.replace("-", "").replace("_", "").isalnum():
            ids.add(element_id)
    return frozenset(ids)


def unparsed_select_oob_tokens(select_oob: str | None) -> frozenset[str]:
    """Return ``hx-select-oob`` tokens that are not simple ``#id`` selectors.

    Hedron's conflict scanner only understands ``#id`` lists. Attribute or
    descendant selectors are returned here so hosts can warn or document the
    limitation.
    """
    if not select_oob:
        return frozenset()
    unparsed: set[str] = set()
    for part in select_oob.split(","):
        token = part.strip()
        if not token:
            continue
        if not safe_css_selector(token) or not token.startswith("#"):
            unparsed.add(token)
            continue
        element_id = token[1:]
        if not element_id.replace("-", "").replace("_", "").isalnum():
            unparsed.add(token)
    return frozenset(unparsed)


def oob_update_element_ids(oob: Sequence[OobUpdate] | None) -> frozenset[str]:
    """Return element ids that ``OobUpdate`` values will bind for ``hx-swap-oob``."""
    if not oob:
        return frozenset()
    ids: set[str] = set()
    for update in oob:
        bound = _bound_oob_element_id(update, regions=())
        if bound is not None:
            ids.add(bound)
    return frozenset(ids)


def conflicting_select_oob_targets(
    select_oob: str | None,
    oob: Sequence[OobUpdate] | None = None,
    *,
    oob_ids: frozenset[str] | set[str] | None = None,
) -> frozenset[str]:
    """Return ids targeted by both ``hx-select-oob`` and server ``OobUpdate``.

    Use one mechanism per target. Prefer explicit ``OobUpdate`` (omit matching
    ``select_oob``) so ``innerHTML`` swaps preserve semantic shell hosts.
    """
    selected = parse_select_oob_element_ids(select_oob)
    if not selected:
        return frozenset()
    bound = frozenset(oob_ids) if oob_ids is not None else oob_update_element_ids(oob)
    return frozenset(selected & bound)


def oob_swap(
    element_id: str,
    content: NodeLike,
    *,
    swap: str = "innerHTML",
    tag: OobEnvelopeTag = "div",
) -> NodeLike:
    """Mark a node for HTMX out-of-band swap via hx-swap-oob (framework-neutral)."""
    if not element_id.replace("-", "").replace("_", "").isalnum():
        raise ValueError("Unsafe OOB element id")
    if tag not in OOB_ENVELOPE_TAGS:
        raise ValueError(
            f"Unsupported OOB envelope tag={tag!r}; allowlisted: {sorted(OOB_ENVELOPE_TAGS)}"
        )
    from hedron_core.html import html

    return getattr(html, tag)(content, id=element_id, **{"hx-swap-oob": swap})


def _bound_oob_element_id(
    update: OobUpdate,
    *,
    regions: tuple[FragmentRegion, ...],
) -> str | None:
    del regions  # regions authorize; id binding uses element_id / #select.
    if update.element_id is not None:
        return update.element_id
    # Derive from #select even when regions are empty so reserved OOB sinks
    # (toast/chrome) always get a forced hx-swap-oob wrapper.
    if update.select and update.select.startswith("#"):
        return update.select[1:]
    return None


def materialize_interaction_nodes(result: InteractionResult) -> NodeLike | None:
    """Authorize OOB updates and return a renderable node tree (or None)."""
    from hedron_core.builtins import Fragment

    regions = result.policy.declared_regions if result.policy is not None else ()
    if not result.oob:
        return result.content
    nodes: list[NodeLike] = []
    if result.content is not None:
        nodes.append(result.content)
    for update in result.oob:
        authorize_oob_update(update, regions=regions)
        bound_id = _bound_oob_element_id(update, regions=regions)
        if bound_id is not None:
            # Always wrap to the authorized id so caller content cannot emit a
            # different hx-swap-oob target under declared regions.
            node: NodeLike = oob_swap(
                bound_id,
                update.content,
                swap=update.swap,
                tag=update.tag,
            )
        else:
            node = update.content
        nodes.append(node)
    if not nodes:
        return None
    if len(nodes) == 1:
        return nodes[0]
    return Fragment(*nodes)
