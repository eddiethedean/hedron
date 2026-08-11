"""Optional chart hosts purge on htmx:beforeSwap and register on document."""

from __future__ import annotations

from pathlib import Path

_ASSETS = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "hedron-charts"
    / "src"
    / "hedron_charts"
    / "assets"
)
_HOSTS = (
    "echarts/host.js",
    "chartjs/host.js",
    "maplibre/host.js",
    "mermaid/host.js",
    "static/host.js",
    "plotly/host.js",
    "vega/host.js",
)


def test_chart_hosts_register_document_htmx_lifecycle() -> None:
    for rel in _HOSTS:
        text = (_ASSETS / rel).read_text(encoding="utf-8")
        assert "htmx:beforeSwap" in text, rel
        assert 'document.addEventListener("htmx:beforeSwap"' in text or (
            "document.addEventListener('htmx:beforeSwap'" in text
        ), rel
        assert "document.body &&" not in text, rel
        assert "beforeSwap" in text, rel
