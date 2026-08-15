"""HTMX / fragment interaction types and policy."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from typing import Any, Literal

from hedron_core.component import NodeLike
from hedron_core.htmx_contract import HtmxContext, safe_hx_swap
from hedron_core.typing_aliases import HxLocation, JsonValue

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
        if not safe_hx_swap(self.swap):
            raise ValueError(f"Unsafe OobUpdate swap value: {self.swap!r}")


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
            authorized declared region (via ``resolve_fragment_region`` helpers),
            or when outbound ``HX-Retarget`` / ``HX-Reselect`` escape the route
            allowlist (via ``interaction_headers``).

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
    # Request-side hx-select-oob when known (same-target conflict detection).
    select_oob: str | None = None

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
        if self.select_oob is not None:
            from hedron_core.htmx.oob import unparsed_select_oob_tokens

            unparsed = unparsed_select_oob_tokens(self.select_oob)
            if unparsed:
                tokens = ", ".join(sorted(unparsed))
                raise ValueError(
                    f"select_oob must use simple #id selectors only; unsupported token(s): {tokens}"
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
