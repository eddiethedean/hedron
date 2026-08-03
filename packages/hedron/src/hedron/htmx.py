"""HTMX request detection and approved response headers."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from starlette.requests import Request

from hedron_core.rendering import RenderMode

__all__ = [
    "HtmxContext",
    "approved_headers",
    "is_htmx_request",
    "render_mode_for_request",
]

APPROVED_REQUEST_HEADERS = frozenset(
    {
        "HX-Request",
        "HX-Target",
        "HX-Trigger",
        "HX-Trigger-Name",
        "HX-Current-URL",
        "HX-Prompt",
        "HX-Boosted",
        "HX-History-Restore-Request",
    }
)

APPROVED_RESPONSE_HEADERS = frozenset(
    {
        "HX-Location",
        "HX-Push-Url",
        "HX-Redirect",
        "HX-Refresh",
        "HX-Replace-Url",
        "HX-Reswap",
        "HX-Retarget",
        "HX-Reselect",
        "HX-Trigger",
        "HX-Trigger-After-Settle",
        "HX-Trigger-After-Swap",
    }
)


@dataclass(frozen=True, slots=True)
class HtmxContext:
    is_htmx: bool
    target: str | None = None
    trigger: str | None = None
    current_url: str | None = None
    boosted: bool = False
    history_restore: bool = False
    extras: Mapping[str, str] = field(default_factory=dict)


def is_htmx_request(request: Request) -> bool:
    return request.headers.get("HX-Request", "").lower() == "true"


def htmx_context(request: Request) -> HtmxContext:
    if not is_htmx_request(request):
        return HtmxContext(is_htmx=False)
    extras = {
        key: value
        for key, value in request.headers.items()
        if key in APPROVED_REQUEST_HEADERS and key not in {"HX-Request", "HX-Target", "HX-Trigger"}
    }
    return HtmxContext(
        is_htmx=True,
        target=request.headers.get("HX-Target"),
        trigger=request.headers.get("HX-Trigger"),
        current_url=request.headers.get("HX-Current-URL"),
        boosted=request.headers.get("HX-Boosted", "").lower() == "true",
        history_restore=request.headers.get("HX-History-Restore-Request", "").lower() == "true",
        extras=extras,
    )


def render_mode_for_request(request: Request, *, force: RenderMode | None = None) -> RenderMode:
    if force is not None:
        return force
    return RenderMode.FRAGMENT if is_htmx_request(request) else RenderMode.PAGE


def approved_headers(
    *,
    trigger: str | Mapping[str, Any] | None = None,
    redirect: str | None = None,
    push_url: str | bool | None = None,
    refresh: bool = False,
    retarget: str | None = None,
    reswap: str | None = None,
    location: str | Mapping[str, Any] | None = None,
) -> dict[str, str]:
    headers: dict[str, str] = {}
    if trigger is not None:
        headers["HX-Trigger"] = trigger if isinstance(trigger, str) else json.dumps(trigger)
    if redirect is not None:
        if not redirect.startswith("/") or redirect.startswith("//"):
            raise ValueError("HX-Redirect must be a local path")
        headers["HX-Redirect"] = redirect
    if push_url is not None:
        if push_url is False:
            headers["HX-Push-Url"] = "false"
        elif push_url is True:
            headers["HX-Push-Url"] = "true"
        else:
            headers["HX-Push-Url"] = str(push_url)
    if refresh:
        headers["HX-Refresh"] = "true"
    if retarget is not None:
        if not _safe_css_selector(retarget):
            raise ValueError("Unsafe HTMX retarget selector")
        headers["HX-Retarget"] = retarget
    if reswap is not None:
        headers["HX-Reswap"] = reswap
    if location is not None:
        headers["HX-Location"] = location if isinstance(location, str) else json.dumps(location)
    unknown = set(headers) - APPROVED_RESPONSE_HEADERS
    if unknown:
        raise ValueError(f"Unapproved HTMX response headers: {sorted(unknown)}")
    return headers


def _safe_css_selector(selector: str) -> bool:
    if not selector or any(ch in selector for ch in "<>\"'`"):
        return False
    return selector.startswith("#") or selector.startswith(".") or selector.startswith("[")
