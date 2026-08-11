"""Optional chart hosts purge on htmx:beforeSwap and register on document."""

from __future__ import annotations

import re
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

# destroy(el) must run before remount work (payload parse / newPlot / embed).
_DESTROY_BEFORE_MOUNT = re.compile(
    r"function\s+mount\s*\(\s*el\s*\)\s*\{(?P<body>.*?)\n\s*function\s+",
    re.DOTALL,
)


def test_chart_hosts_register_document_htmx_lifecycle() -> None:
    for rel in _HOSTS:
        text = (_ASSETS / rel).read_text(encoding="utf-8")
        assert "htmx:beforeSwap" in text, rel
        assert 'document.addEventListener("htmx:beforeSwap"' in text or (
            "document.addEventListener('htmx:beforeSwap'" in text
        ), rel
        assert "htmx:oobBeforeSwap" in text, rel
        assert "htmx:oobAfterSwap" in text, rel
        assert "htmx:load" in text, rel
        assert "document.body &&" not in text, rel
        assert "beforeSwap" in text, rel


def test_plotly_vega_guard_stale_async_mount() -> None:
    plotly = (_ASSETS / "plotly/host.js").read_text(encoding="utf-8")
    vega = (_ASSETS / "vega/host.js").read_text(encoding="utf-8")
    assert "_hedronPlotlyGen" in plotly
    assert "el._hedronPlotlyGen !== gen" in plotly
    assert "_hedronVegaGen" in vega
    assert "el._hedronVegaGen !== gen" in vega


def test_maplibre_coord_order_and_load_guard() -> None:
    text = (_ASSETS / "maplibre/host.js").read_text(encoding="utf-8")
    assert "coord_order" in text
    assert "lnglat" in text
    assert "_hedronMapGen" in text
    assert "el._hedronMapLibre !== map" in text


def test_mermaid_initialize_once() -> None:
    text = (_ASSETS / "mermaid/host.js").read_text(encoding="utf-8")
    assert "var initialized = false" in text
    assert "if (!initialized)" in text
    assert text.count("mermaid.initialize") == 1


def test_chart_hosts_dispose_and_scan_include_self_target() -> None:
    """querySelectorAll skips the root; self-targeted swaps need matches()."""
    for rel in _HOSTS:
        text = (_ASSETS / rel).read_text(encoding="utf-8")
        assert ".matches(" in text, rel
        assert "querySelectorAll" in text, rel
        # Dispose path must consider the swap target itself.
        assert "target.matches" in text, rel
        # Remount path must consider the afterSwap root itself.
        assert "base.matches" in text, rel


def test_chart_hosts_destroy_before_mount() -> None:
    """Remounts without a prior HTMX dispose must not stack runtimes/handlers."""
    for rel in _HOSTS:
        text = (_ASSETS / rel).read_text(encoding="utf-8")
        match = _DESTROY_BEFORE_MOUNT.search(text)
        assert match is not None, f"{rel}: could not locate mount() body"
        body = match.group("body")
        # First meaningful statement should destroy the prior instance.
        assert re.search(r"^\s*destroy\s*\(\s*el\s*\)\s*;", body, re.MULTILINE), rel
        assert "Plotly.newPlot" not in body.split("destroy(el)", 1)[0]
        assert "vegaEmbed" not in body.split("destroy(el)", 1)[0]
