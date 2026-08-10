"""Typed FastAPI/HTMX interaction envelope (adapter over portable core types)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from starlette.requests import Request

from hedron.htmx import htmx_context, is_htmx_request
from hedron_core.component import NodeLike
from hedron_core.htmx_contract import HtmxContext
from hedron_core.interaction import (
    FragmentRegion,
    FragmentRegionError,
    HtmxRequestFacts,
    InteractionPolicy,
    InteractionResult,
    OobUpdate,
    StatusPolicy,
    authorize_oob_update,
    default_interaction_policy,
    form_sync_attrs,
    interaction_trace,
    merge_route_regions,
    resolve_fragment_region,
    status_policy_for,
)
from hedron_core.interaction import (
    interaction_headers as portable_interaction_headers,
)

__all__ = [
    "FragmentRegion",
    "FragmentRegionError",
    "HtmxRequest",
    "InteractionPolicy",
    "InteractionResult",
    "OobUpdate",
    "StatusPolicy",
    "authorize_oob_update",
    "default_interaction_policy",
    "form_sync_attrs",
    "htmx_request",
    "interaction_headers",
    "merge_route_regions",
    "redirect_htmx",
    "resolve_fragment_region",
    "retarget",
    "status_policy_for",
    "swap",
    "swap_oob",
]


@dataclass(frozen=True, slots=True)
class HtmxRequest:
    """FastAPI-bound wrapper retaining the raw Request for adapter helpers."""

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

    def facts(self) -> HtmxRequestFacts:
        return HtmxRequestFacts(context=self.context)


def htmx_request(request: Request) -> HtmxRequest:
    return HtmxRequest(request=request, context=htmx_context(request))


def interaction_headers(
    result: InteractionResult,
    *,
    request: Request | None = None,
) -> dict[str, str]:
    headers = portable_interaction_headers(result)
    if request is not None and is_htmx_request(request):
        request.state.hedron_interaction = interaction_trace(result)
    return headers


def _coerce_oob(item: OobUpdate | NodeLike) -> OobUpdate:
    if isinstance(item, OobUpdate):
        return item
    return OobUpdate(content=item)


def swap(
    content: NodeLike | None,
    *,
    toast: str | NodeLike | OobUpdate | None = None,
    oob: Sequence[OobUpdate | NodeLike] = (),
    **kwargs: Any,
) -> InteractionResult:
    """Build a primary-fragment :class:`InteractionResult` (optional toast / OOB)."""
    updates = [_coerce_oob(item) for item in oob]
    if toast is not None:
        if isinstance(toast, OobUpdate):
            updates.append(toast)
        elif isinstance(toast, str):
            from hedron_core.builtins import Toast

            updates.append(OobUpdate(content=Toast(toast), element_id="hedron-toast"))
        else:
            updates.append(OobUpdate(content=toast, element_id="hedron-toast"))
    return InteractionResult(content=content, oob=tuple(updates), **kwargs)


def swap_oob(
    content: NodeLike | None,
    *oob: OobUpdate | NodeLike,
    **kwargs: Any,
) -> InteractionResult:
    """Primary fragment plus one or more out-of-band updates."""
    existing = list(kwargs.pop("oob", ()) or ())
    updates = [_coerce_oob(item) for item in (*oob, *existing)]
    return InteractionResult(content=content, oob=tuple(updates), **kwargs)


def retarget(
    content: NodeLike | None,
    region: FragmentRegion | str,
    **kwargs: Any,
) -> InteractionResult:
    """Return content with an approved ``HX-Retarget`` selector."""
    if isinstance(region, FragmentRegion):
        selector = region.selector
        # Prefer the CSS selector for HX-Target agreement when id differs from selector.
        kwargs.setdefault("region_id", selector)
    else:
        selector = str(region)
    return InteractionResult(content=content, retarget=selector, **kwargs)


def redirect_htmx(url: str) -> InteractionResult:
    """Issue an HTMX ``HX-Redirect`` via :class:`InteractionResult`."""
    return InteractionResult(redirect=url)
