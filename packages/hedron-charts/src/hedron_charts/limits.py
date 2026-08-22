"""Shared chart helpers: limits, redaction, missing-extra diagnostics."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path

from hedron_core.diagnostics import HedronError, error
from hedron_core.security import contains_dangerous_scheme
from hedron_core.security.urls import nfkc_strip_format
from hedron_core.typing_aliases import JsonObject, JsonValue
from hedron_core.visualization import (
    DEFAULT_MAX_CHART_ROWS,
    DEFAULT_MAX_PAYLOAD_BYTES,
    ChartAccessibility,
    VisualizationLimits,
)

__all__ = [
    "ensure_limits",
    "missing_extra",
    "payload_size",
    "redact_rows",
    "reject_active_svg",
    "reject_callbacks",
    "reject_remote_urls",
]


@lru_cache(maxsize=1)
def _pypi_pin_bounds() -> tuple[str, str]:
    """Read deferred-honesty pin from docs/release.toml when present in-tree."""
    import tomllib

    # packages/hedron-charts/src/hedron_charts/limits.py → repo root is parents[4]
    path = Path(__file__).resolve().parents[4] / "docs" / "release.toml"
    if not path.is_file():
        return "0.52.0", "0.53"
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    release = data.get("release") or {}
    floor = str(release.get("pypi_pin_floor") or release.get("pin_floor") or "0.52.0").strip()
    ceiling = str(release.get("pypi_pin_ceiling") or release.get("pin_ceiling") or "0.53").strip()
    return floor, ceiling


def missing_extra(extra: str, *, package: str = "hedron-charts") -> HedronError:
    floor, ceiling = _pypi_pin_bounds()
    return error(
        "HED-CHART-0001",
        title=f"Missing optional dependency: {extra}",
        explanation=f"This chart adapter requires the {extra!r} extra.",
        remediation=(
            f'Install with: pip install "{package}[{extra}]>=0.2.0,<0.3" or '
            f'pip install "hedron[charts]>={floor},<{ceiling}".'
        ),
    )


def ensure_limits(
    rows: Sequence[object] | None,
    payload: str | bytes | None,
    *,
    limits: VisualizationLimits | None = None,
) -> VisualizationLimits:
    lim = limits or VisualizationLimits()
    if rows is not None and len(rows) > lim.max_rows:
        raise error(
            "HED-CHART-0002",
            title="Chart row limit exceeded",
            explanation=f"Received {len(rows)} rows; max is {lim.max_rows}.",
            remediation="Aggregate server-side or raise VisualizationLimits.max_rows explicitly.",
        )
    checked_payload = payload
    if checked_payload is None and rows is not None:
        # Beginner ChartSpec paths pass rows only; still enforce the byte budget on
        # the serialized tabular payload (same HED-CHART-0003 contract as hosts).
        checked_payload = json.dumps(list(rows), default=str, separators=(",", ":"))
    if checked_payload is not None:
        size = payload_size(checked_payload)
        if size > lim.max_payload_bytes:
            raise error(
                "HED-CHART-0003",
                title="Chart payload limit exceeded",
                explanation=f"Payload is {size} bytes; max is {lim.max_payload_bytes}.",
                remediation=(
                    "Reduce figure complexity or raise VisualizationLimits.max_payload_bytes."
                ),
            )
    return lim


def payload_size(payload: str | bytes) -> int:
    if isinstance(payload, bytes):
        return len(payload)
    return len(payload.encode("utf-8"))


# Exact sensitive column names only — avoid substring false-positives (#192).
_SENSITIVE_KEYS = frozenset(
    {
        "secret",
        "password",
        "passwd",
        "token",
        "api_key",
        "apikey",
        "access_token",
        "refresh_token",
        "private_key",
        "client_secret",
    }
)


def redact_rows(rows: Sequence[Mapping[str, JsonValue]]) -> list[JsonObject]:
    out: list[JsonObject] = []
    for row in rows:
        cleaned: JsonObject = {}
        for key, value in row.items():
            if str(key).lower() in _SENSITIVE_KEYS:
                cleaned[str(key)] = "***"
            else:
                cleaned[str(key)] = value  # JsonValue from input mapping
        out.append(cleaned)
    return out


_HTML_HANDLER = (
    "onclick=",
    "onload=",
    "onerror=",
    "onmouseover=",
    "onfocus=",
    "onmouseenter=",
    "<script",
)


def reject_callbacks(obj: object) -> None:
    if _walk_callbacks(obj):
        raise error(
            "HED-CHART-0004",
            title="Executable chart callbacks rejected",
            explanation="Raw JavaScript callbacks are not allowed in chart specifications.",
            remediation="Remove callbacks and use server-side HTMX actions instead.",
        )
    text = obj if isinstance(obj, str) else json.dumps(obj, default=str)
    lowered = text.lower()
    if (
        "function(" in lowered
        or "javascript:" in lowered
        or ('"click"' in lowered and "callback" in lowered)
        or any(token in lowered for token in _HTML_HANDLER)
    ):
        raise error(
            "HED-CHART-0004",
            title="Executable chart callbacks rejected",
            explanation="Raw JavaScript callbacks are not allowed in chart specifications.",
            remediation="Remove callbacks and use server-side HTMX actions instead.",
        )


def _walk_callbacks(obj: object) -> bool:
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            key_l = str(key).lower()
            if key_l.startswith("on") and len(key_l) > 2:
                return True
            if key_l in {"callback", "callbacks", "js", "javascript", "formatter", "hovertemplate"}:
                if isinstance(value, str) and _string_looks_executable(value):
                    return True
                if key_l in {"callback", "callbacks", "js", "javascript"}:
                    return True
            if _walk_callbacks(value):
                return True
    elif isinstance(obj, (list, tuple)):
        return any(_walk_callbacks(item) for item in obj)
    elif isinstance(obj, str):
        return _string_looks_executable(obj)
    return False


def _string_looks_executable(value: str) -> bool:
    lowered = nfkc_strip_format(value).lower()
    return (
        "function(" in lowered
        or "javascript:" in lowered
        or contains_dangerous_scheme(value)
        or any(token in lowered for token in _HTML_HANDLER)
    )


def reject_remote_urls(obj: object) -> None:
    if _walk_remote(obj) or (isinstance(obj, str) and _is_remote_url(obj)):
        raise error(
            "HED-CHART-0005",
            title="Remote chart assets rejected",
            explanation="Unapproved remote URLs are not allowed in chart payloads.",
            remediation="Use locally registered Hedron assets and offline runtimes.",
        )


_REMOTE_ASSET_KEYS = frozenset(
    {
        "url",
        "href",
        "src",
        "source",
        "image",
        # Plotly Mapbox / media asset keys that commonly hold remote URLs (#592).
        "style",
        "icon",
        "logo",
        "poster",
        "tiles",
        "tilejson",
    }
)


def _walk_remote(obj: object) -> bool:
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            key_l = str(key).lower()
            if (
                key_l in _REMOTE_ASSET_KEYS
                and isinstance(value, str)
                and _is_remote_url(value)
            ):
                return True
            if _walk_remote(value):
                return True
    elif isinstance(obj, (list, tuple)):
        return any(_walk_remote(item) for item in obj)
    return False


_UNSAFE_ASSET_SCHEMES = (
    "data:",
    "file:",
    "javascript:",
    "vbscript:",
    "blob:",
    "about:",
)


def _is_remote_url(value: str) -> bool:
    lowered = nfkc_strip_format(value).lower().strip()
    # These schemes are unsafe in asset positions even though they do not all name
    # a remote host. Chart specifications must use registered local assets instead.
    if lowered.startswith(_UNSAFE_ASSET_SCHEMES) or contains_dangerous_scheme(value):
        return True
    return (
        lowered.startswith("http://")
        or lowered.startswith("https://")
        or lowered.startswith("//")
        or "//cdn." in lowered
    )


def reject_active_svg(svg: str) -> None:
    """Reject script tags and common SVG event/active-content patterns."""
    from hedron_core.active_markup import active_markup_reason

    reason = active_markup_reason(svg)
    if reason is not None:
        raise error(
            "HED-CHART-0006",
            title="Active SVG content rejected",
            explanation=f"Chart SVG rejected ({reason}).",
            remediation="Sanitize SVG before rendering or use TrustedHtml.nh3(...).",
        )


def accessibility_or_raise(
    *,
    title: str,
    description: str | None = None,
    alt: str | None = None,
    waiver: str | None = None,
    tabular_fallback: Sequence[Mapping[str, JsonValue]] | None = None,
) -> ChartAccessibility:
    return ChartAccessibility(
        title=title,
        description=description,
        alt=alt,
        waiver=waiver,
        tabular_fallback=tabular_fallback,
    ).validated()


# Re-export defaults for adapters
MAX_ROWS = DEFAULT_MAX_CHART_ROWS
MAX_PAYLOAD = DEFAULT_MAX_PAYLOAD_BYTES
