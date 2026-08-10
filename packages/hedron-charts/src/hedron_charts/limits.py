"""Shared chart helpers: limits, redaction, missing-extra diagnostics."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence

from hedron_core.diagnostics import HedronError, error
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


def missing_extra(extra: str, *, package: str = "hedron-charts") -> HedronError:
    return error(
        "HED-CHART-0001",
        title=f"Missing optional dependency: {extra}",
        explanation=f"This chart adapter requires the {extra!r} extra.",
        remediation=(
            f'Install with: pip install "{package}[{extra}]>=0.1.6,<0.2" or '
            f'pip install "hedron[charts]>=0.27.0,<0.28".'
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
    if payload is not None:
        size = payload_size(payload)
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


def redact_rows(rows: Sequence[Mapping[str, JsonValue]]) -> list[JsonObject]:
    out: list[JsonObject] = []
    for row in rows:
        cleaned: JsonObject = {}
        for key, value in row.items():
            if "secret" in str(key).lower() or "password" in str(key).lower():
                cleaned[str(key)] = "***"
            else:
                cleaned[str(key)] = value  # JsonValue from input mapping
        out.append(cleaned)
    return out


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
            if key_l in {"callback", "callbacks", "js", "javascript"}:
                return True
            if _walk_callbacks(value):
                return True
    elif isinstance(obj, (list, tuple)):
        return any(_walk_callbacks(item) for item in obj)
    elif isinstance(obj, str):
        lowered = obj.lower()
        return "function(" in lowered or "javascript:" in lowered
    return False


def reject_remote_urls(obj: object) -> None:
    if _walk_remote(obj):
        raise error(
            "HED-CHART-0005",
            title="Remote chart assets rejected",
            explanation="Unapproved remote URLs are not allowed in chart payloads.",
            remediation="Use locally registered Hedron assets and offline runtimes.",
        )


def _walk_remote(obj: object) -> bool:
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            key_l = str(key).lower()
            if (
                key_l in {"url", "href", "src", "source", "image"}
                and isinstance(value, str)
                and _is_remote_url(value)
            ):
                return True
            if _walk_remote(value):
                return True
    elif isinstance(obj, (list, tuple)):
        return any(_walk_remote(item) for item in obj)
    elif isinstance(obj, str):
        return _is_remote_url(obj) and (
            obj.lower().startswith("data:")
            or "http://" in obj.lower()
            or "https://" in obj.lower()
            or "//cdn." in obj.lower()
        )
    return False


def _is_remote_url(value: str) -> bool:
    lowered = value.lower().strip()
    # data: payloads are not http(s) remote hosts, but they are still disallowed in
    # chart specs (SVG/script hosts must not embed arbitrary data URLs).
    if lowered.startswith("data:"):
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
