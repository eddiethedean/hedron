"""Request-bound interaction header assembly."""

from __future__ import annotations

from starlette.requests import Request

from hedron.htmx import is_htmx_request
from hedron.interaction._core import (
    InteractionResult,
    interaction_trace,
    portable_interaction_headers,
)

__all__ = ["interaction_headers"]


def interaction_headers(
    result: InteractionResult,
    *,
    request: Request | None = None,
) -> dict[str, str]:
    headers = portable_interaction_headers(result)
    if request is not None and is_htmx_request(request):
        request.state.hedron_interaction = interaction_trace(result)
    return headers
