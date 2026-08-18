"""Portable HTMX header allowlists and approved response builders (framework-neutral)."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from urllib.parse import urlparse

from hedron_core.typing_aliases import HxLocation, HxTriggerPayload, JsonValue

__all__ = [
    "APPROVED_REQUEST_HEADERS",
    "APPROVED_RESPONSE_HEADERS",
    "HtmxContext",
    "approved_headers",
    "htmx_context_from_headers",
    "is_local_path",
    "safe_css_selector",
    "safe_hx_swap",
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

_LOCAL_PATH = re.compile(r"^/[A-Za-z0-9._~!$&'()*+,;=:@%/\-]*$")
_SIMPLE_SELECTOR = re.compile(
    r"^(?:#[A-Za-z_][\w\-]*|\.[A-Za-z_][\w\-]*|\[[A-Za-z_][\w\-]*(?:=(?:"
    r'"[^"]*"|\'[^\']*\'|[A-Za-z0-9_\-]+))?\])$'
)
_ON_ATTR = re.compile(r"^on[a-z]+$", re.IGNORECASE)
_HX_SWAP_STYLES = frozenset(
    {
        "innerHTML",
        "outerHTML",
        "textContent",
        "beforebegin",
        "afterbegin",
        "beforeend",
        "afterend",
        "delete",
        "none",
    }
)
_HX_SWAP_MODIFIERS = frozenset(
    {
        "settle",
        "swap",
        "focus-scroll",
        "show",
        "scroll",
        "transition",
        "ignoreTitle",
    }
)
_HX_LOCATION_KEYS = frozenset({"path", "target", "select", "swap", "values"})
_DECODE_ROUNDS = 8


def _empty_headers() -> dict[str, str]:
    return {}


@dataclass(frozen=True, slots=True)
class HtmxContext:
    """Portable HTMX request facts (no raw framework request object)."""

    is_htmx: bool
    target: str | None = None
    trigger: str | None = None
    trigger_name: str | None = None
    current_url: str | None = None
    prompt: str | None = None
    boosted: bool = False
    history_restore: bool = False
    extras: Mapping[str, str] = field(default_factory=_empty_headers)


def _path_has_traversal(candidate: str) -> bool:
    lowered = candidate.lower()
    if "%2e%2e" in lowered or "%2e." in lowered or ".%2e" in lowered:
        return True
    # Normalize semicolon-smuggled segments such as "/..;/etc".
    normalized = candidate.replace(";", "/")
    parts = [p for p in normalized.split("/") if p not in {"", "."}]
    return any(part == ".." or part.startswith("..") for part in parts)


def is_local_path(url: str) -> bool:
    """Same-origin relative path check used by approved redirect/location headers."""
    from urllib.parse import unquote

    if "\\" in url or any(ord(ch) < 32 for ch in url):
        return False
    decoded = url
    for _ in range(_DECODE_ROUNDS):
        next_decoded = unquote(decoded)
        if next_decoded == decoded:
            break
        decoded = next_decoded
        if "\\" in decoded or any(ord(ch) < 32 for ch in decoded):
            return False
        if decoded.startswith("//") or "://" in decoded:
            return False
    if url.startswith("//") or "://" in url:
        return False
    if decoded.startswith("//") or "://" in decoded:
        return False
    parsed = urlparse(url)
    if parsed.scheme or parsed.netloc:
        return False
    if not url.startswith("/") or url.startswith("//"):
        return False
    if decoded.startswith("//"):
        return False
    path = parsed.path or "/"
    decoded_path = urlparse(decoded).path or "/"
    for candidate in (path, decoded_path, url, decoded):
        if _path_has_traversal(candidate):
            return False
    return (
        _LOCAL_PATH.fullmatch(path) is not None and _LOCAL_PATH.fullmatch(decoded_path) is not None
    )


def safe_css_selector(selector: str) -> bool:
    """Allow only a single simple #id, .class, or [attr=value] selector."""
    if not selector or any(ch in selector for ch in "<>`);{}\\"):
        return False
    text = selector.strip()
    if not text or any(ch.isspace() for ch in text):
        return False
    if any(token in text for token in (",", "*", ">", "+", "~", "/", ":")):
        return False
    if not _SIMPLE_SELECTOR.fullmatch(text):
        return False
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1]
        attr = inner.split("=", 1)[0]
        if _ON_ATTR.fullmatch(attr):
            return False
    return True


def safe_hx_swap(value: str) -> bool:
    """Allow only HTMX swap styles and known modifiers."""
    if not value or any(ord(ch) < 32 for ch in value) or '"' in value or "'" in value:
        return False
    tokens = value.split()
    if not tokens:
        return False
    if tokens[0] not in _HX_SWAP_STYLES:
        return False
    for token in tokens[1:]:
        name, sep, _rest = token.partition(":")
        if not sep or name not in _HX_SWAP_MODIFIERS:
            return False
    return True


def htmx_context_from_headers(headers: Mapping[str, str]) -> HtmxContext:
    def get(name: str) -> str | None:
        lower = {k.lower(): v for k, v in headers.items()}
        return lower.get(name.lower())

    is_htmx = (get("HX-Request") or "").lower() == "true"
    extras: dict[str, str] = {}
    for key in APPROVED_REQUEST_HEADERS - {"HX-Request", "HX-Target", "HX-Trigger"}:
        value = get(key)
        if value is not None:
            extras[key] = value
    return HtmxContext(
        is_htmx=is_htmx,
        target=get("HX-Target"),
        trigger=get("HX-Trigger"),
        trigger_name=get("HX-Trigger-Name"),
        current_url=get("HX-Current-URL"),
        prompt=get("HX-Prompt"),
        boosted=(get("HX-Boosted") or "").lower() == "true",
        history_restore=(get("HX-History-Restore-Request") or "").lower() == "true",
        extras=extras,
    )


def _require_local_path(url: str, header_name: str) -> str:
    if not is_local_path(url):
        raise ValueError(f"{header_name} must be a local path")
    return url


def _validate_location_mapping(
    location: Mapping[str, JsonValue] | HxLocation,
) -> dict[str, JsonValue]:
    unknown = set(location) - _HX_LOCATION_KEYS
    if unknown:
        raise ValueError(f"Unapproved HX-Location keys: {sorted(unknown)}")
    path = location.get("path")
    if not isinstance(path, str):
        raise ValueError("HX-Location mapping requires a local path")
    _require_local_path(path, "HX-Location")
    cleaned: dict[str, JsonValue] = {"path": path}
    target = location.get("target")
    if target is not None:
        if not isinstance(target, str) or not safe_css_selector(target):
            raise ValueError("Unsafe HX-Location target selector")
        cleaned["target"] = target
    select = location.get("select")
    if select is not None:
        if not isinstance(select, str) or not safe_css_selector(select):
            raise ValueError("Unsafe HX-Location select selector")
        cleaned["select"] = select
    swap = location.get("swap")
    if swap is not None:
        if not isinstance(swap, str) or not safe_hx_swap(swap):
            raise ValueError("Unsafe HX-Location swap value")
        cleaned["swap"] = swap
    values = location.get("values")
    if values is not None:
        if not isinstance(values, Mapping):
            raise ValueError("HX-Location values must be a mapping")
        cleaned["values"] = dict(values)
    return cleaned


def approved_headers(
    *,
    trigger: HxTriggerPayload | Mapping[str, JsonValue] | None = None,
    trigger_after_swap: HxTriggerPayload | Mapping[str, JsonValue] | None = None,
    trigger_after_settle: HxTriggerPayload | Mapping[str, JsonValue] | None = None,
    redirect: str | None = None,
    push_url: str | bool | None = None,
    replace_url: str | bool | None = None,
    refresh: bool = False,
    retarget: str | None = None,
    reswap: str | None = None,
    reselect: str | None = None,
    location: str | HxLocation | Mapping[str, JsonValue] | None = None,
) -> dict[str, str]:
    headers: dict[str, str] = {}
    if trigger is not None:
        headers["HX-Trigger"] = trigger if isinstance(trigger, str) else json.dumps(trigger)
    if trigger_after_swap is not None:
        headers["HX-Trigger-After-Swap"] = (
            trigger_after_swap
            if isinstance(trigger_after_swap, str)
            else json.dumps(trigger_after_swap)
        )
    if trigger_after_settle is not None:
        headers["HX-Trigger-After-Settle"] = (
            trigger_after_settle
            if isinstance(trigger_after_settle, str)
            else json.dumps(trigger_after_settle)
        )
    if redirect is not None:
        headers["HX-Redirect"] = _require_local_path(redirect, "HX-Redirect")
    if push_url is not None:
        if push_url is False:
            headers["HX-Push-Url"] = "false"
        elif push_url is True:
            headers["HX-Push-Url"] = "true"
        else:
            headers["HX-Push-Url"] = _require_local_path(str(push_url), "HX-Push-Url")
    if replace_url is not None:
        if replace_url is False:
            headers["HX-Replace-Url"] = "false"
        elif replace_url is True:
            headers["HX-Replace-Url"] = "true"
        else:
            headers["HX-Replace-Url"] = _require_local_path(str(replace_url), "HX-Replace-Url")
    if refresh:
        headers["HX-Refresh"] = "true"
    if retarget is not None:
        if not safe_css_selector(retarget):
            raise ValueError("Unsafe HTMX retarget selector")
        headers["HX-Retarget"] = retarget
    if reswap is not None:
        if not safe_hx_swap(reswap):
            raise ValueError("Unsafe HTMX reswap value")
        headers["HX-Reswap"] = reswap
    if reselect is not None:
        if not safe_css_selector(reselect):
            raise ValueError("Unsafe HTMX reselect selector")
        headers["HX-Reselect"] = reselect
    if location is not None:
        if isinstance(location, str):
            headers["HX-Location"] = _require_local_path(location, "HX-Location")
        else:
            headers["HX-Location"] = json.dumps(_validate_location_mapping(location))
    unknown = set(headers) - APPROVED_RESPONSE_HEADERS
    if unknown:
        raise ValueError(f"Unapproved HTMX response headers: {sorted(unknown)}")
    for key, value in headers.items():
        if any(ord(ch) < 32 for ch in key) or any(ord(ch) < 32 for ch in value):
            raise ValueError(f"HTMX header {key!r} must not contain control characters")
    return headers
