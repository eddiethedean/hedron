"""Typed FastAPI/HTMX interaction envelope (adapter over portable core types)."""

from __future__ import annotations

from dataclasses import dataclass

from starlette.requests import Request

from hedron.htmx import htmx_context, is_htmx_request
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
    "resolve_fragment_region",
    "status_policy_for",
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
