"""Shared chart helpers: limits, redaction, missing-extra diagnostics."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from hedron_core.diagnostics import HedronError, error
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
    "reject_callbacks",
    "reject_remote_urls",
]


def missing_extra(extra: str, *, package: str = "hedron-charts") -> HedronError:
    return error(
        "HED-CHART-0001",
        title=f"Missing optional dependency: {extra}",
        explanation=f"This chart adapter requires the {extra!r} extra.",
        remediation=(
            f'Install with: pip install "{package}[{extra}]" or pip install "hedron[charts]"'
        ),
    )


def ensure_limits(
    rows: Sequence[Any] | None,
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


def redact_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        cleaned: dict[str, Any] = {}
        for key, value in row.items():
            if "secret" in str(key).lower() or "password" in str(key).lower():
                cleaned[str(key)] = "***"
            else:
                cleaned[str(key)] = value
        out.append(cleaned)
    return out


def reject_callbacks(obj: Any) -> None:
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


def reject_remote_urls(obj: Any) -> None:
    text = obj if isinstance(obj, str) else json.dumps(obj, default=str)
    if "https://" in text or "http://" in text or "//cdn." in text.lower():
        # Allow data: URLs for static images only when already trusted elsewhere.
        raise error(
            "HED-CHART-0005",
            title="Remote chart assets rejected",
            explanation="Unapproved remote URLs are not allowed in chart payloads.",
            remediation="Use locally registered Hedron assets and offline runtimes.",
        )


def accessibility_or_raise(
    *,
    title: str,
    description: str | None = None,
    alt: str | None = None,
    waiver: str | None = None,
    tabular_fallback: Sequence[Mapping[str, Any]] | None = None,
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
