"""Deterministic chart export (EXPORT-038)."""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Mapping
from typing import Any

from hedron_charts.spec import ChartPlan
from hedron_core.diagnostics import error

__all__ = ["export_csv", "export_json", "export_print_html", "export_svg", "plan_export_bundle"]


def _authorized(plan: ChartPlan, kind: str, *, authorized: bool) -> None:
    if not authorized:
        raise error(
            "HED-CHART-0061",
            title="Chart export unauthorized",
            explanation=f"Export kind {kind!r} requires an authorized caller.",
            remediation="Perform authorization server-side before exporting.",
        )
    attr = "json_export" if kind == "json" else kind
    enabled = getattr(plan.export, attr if attr != "print" else "print", False)
    if not enabled:
        raise error(
            "HED-CHART-0062",
            title="Chart export disabled",
            explanation=f"Export kind {kind!r} is disabled by ExportPolicy.",
            remediation="Enable the export kind on ChartSpec.export.",
        )


def export_csv(plan: ChartPlan, *, authorized: bool = True) -> str:
    _authorized(plan, "csv", authorized=authorized)
    rows = list(plan.transformed_rows)
    buf = io.StringIO()
    if not rows:
        return ""
    headers = list(rows[0].keys())
    writer = csv.DictWriter(buf, fieldnames=headers, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({h: row.get(h, "") for h in headers})
    return buf.getvalue()


def export_json(plan: ChartPlan, *, authorized: bool = True) -> str:
    _authorized(plan, "json", authorized=authorized)
    payload = {
        "schema_id": plan.schema_id,
        "spec_fingerprint": plan.spec_fingerprint,
        "data_fingerprint": plan.data_fingerprint,
        "theme": plan.theme.model_dump(mode="json"),
        "rows": list(plan.transformed_rows),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def export_svg(plan: ChartPlan, *, authorized: bool = True, width: int | None = None) -> str:
    _authorized(plan, "svg", authorized=authorized)
    w = width or int(plan.layout.get("width_hint") or 640)
    h = int(plan.layout.get("height_hint") or 360)
    max_px = plan.export.max_px
    if w > max_px or h > max_px:
        raise error(
            "HED-CHART-0063",
            title="Export dimensions exceed bound",
            explanation=f"Requested {w}x{h}; max_px is {max_px}.",
            remediation="Reduce export size.",
        )
    title = plan.accessibility.title
    desc = plan.accessibility.description
    # Deterministic first-party static SVG (semantic equivalence, not pixel identity).
    points = []
    y_values: list[float] = []
    for mark in plan.marks:
        vals = mark.get("values") or {}
        y = vals.get("y")
        try:
            y_values.append(float(y))  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
    y_min = min(0.0, min(y_values)) if y_values else 0.0
    y_max = max(0.0, max(y_values)) if y_values else 1.0
    y_span = y_max - y_min or 1.0
    margin = int(plan.layout.get("margin") or 40)
    plot_w = max(1, w - 2 * margin)
    plot_h = max(1, h - 2 * margin)
    for i, mark in enumerate(plan.marks):
        vals = mark.get("values") or {}
        try:
            y = float(vals.get("y"))  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        x = margin + (i / max(1, len(plan.marks) - 1)) * plot_w if len(plan.marks) > 1 else margin
        t = (y - y_min) / y_span
        py = margin + plot_h - t * plot_h
        py = min(margin + plot_h, max(margin, py))
        points.append(f"{x:.2f},{py:.2f}")
    poly = " ".join(points)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'role="img" aria-labelledby="title desc">'
        f'<title id="title">{_escape(title)}</title>'
        f'<desc id="desc">{_escape(desc)}</desc>'
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="var(--hedron-chart-empty, #fff)"/>'
        f'<polyline fill="none" stroke="var(--hedron-chart-series-1, #2563eb)" '
        f'stroke-width="2" points="{poly}"/>'
        f"</svg>"
    )


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def export_print_html(plan: ChartPlan, *, authorized: bool = True) -> str:
    _authorized(plan, "print", authorized=authorized)
    svg = export_svg(plan, authorized=True)
    summary = _escape(plan.accessibility.summary)
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{_escape(plan.accessibility.title)}</title>"
        "<style>@media print { body { margin: 0; } }</style></head><body>"
        f"<figure>{svg}<figcaption>{summary}</figcaption></figure>"
        "</body></html>"
    )


def plan_export_bundle(plan: ChartPlan, *, authorized: bool = True) -> dict[str, Any]:
    """Return all enabled exports with fingerprints (no remote fetches)."""
    bundle: dict[str, Any] = {
        "spec_fingerprint": plan.spec_fingerprint,
        "data_fingerprint": plan.data_fingerprint,
        "theme": plan.theme.mode,
        "locale": plan.theme.locale,
        "timezone": plan.theme.timezone,
    }
    if plan.export.svg:
        bundle["svg"] = export_svg(plan, authorized=authorized)
    if plan.export.csv:
        bundle["csv"] = export_csv(plan, authorized=authorized)
    if plan.export.json_export:
        bundle["json"] = export_json(plan, authorized=authorized)
    if plan.export.print:
        bundle["print"] = export_print_html(plan, authorized=authorized)
    return bundle


def assert_no_remote_urls(payload: Mapping[str, Any] | str) -> None:
    import re

    text = payload if isinstance(payload, str) else json.dumps(payload)
    # Allow the SVG namespace declaration; reject actual remote fetches.
    cleaned = re.sub(
        r'xmlns\\?=\\?["\']https?://www\.w3\.org/2000/svg\\?["\']',
        "",
        text,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"xmlns=['\"]https?://www\.w3\.org/2000/svg['\"]",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    lowered = cleaned.lower()
    if "http://" in lowered or "https://" in lowered:
        raise error(
            "HED-CHART-0073",
            title="Remote URL in export rejected",
            explanation="Exports must not embed remote fetches.",
            remediation="Use local assets only.",
        )
