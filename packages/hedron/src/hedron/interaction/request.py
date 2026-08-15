"""FastAPI-bound HTMX request wrapper."""

from __future__ import annotations

from dataclasses import dataclass

from starlette.requests import Request

from hedron.htmx import htmx_context
from hedron.interaction._core import HtmxRequestFacts
from hedron_core.htmx_contract import HtmxContext

__all__ = ["HtmxRequest", "htmx_request"]


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
