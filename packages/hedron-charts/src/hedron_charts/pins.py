"""Offline fingerprinted chart runtime pins."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from hedron_core.diagnostics import error
from hedron_core.identifiers import content_digest

_ROOT = Path(__file__).resolve().parent
_ASSETS = _ROOT / "assets"

# Minimum byte sizes that distinguish real minified bundles from comment stubs.
_MIN_BYTES: dict[str, int] = {
    "plotly": 100_000,
    "vega": 50_000,
    "vega-embed": 10_000,
    "chartjs": 50_000,
    "echarts": 50_000,
    "mermaid": 50_000,
    "maplibre": 50_000,
}

__all__ = [
    "RUNTIME_PINS",
    "assert_pins_present",
    "pinned_runtime",
    "refresh_pin_digests",
    "verify_pin",
]


def _digest_file(path: Path) -> str:
    if not path.is_file():
        return "sha256:" + ("0" * 64)
    return content_digest(path.read_bytes())


def _looks_like_stub(path: Path) -> bool:
    if not path.is_file():
        return True
    text = path.read_text(encoding="utf-8", errors="replace")[:200].lower()
    return "pin stub" in text or "supply offline bundle" in text


RUNTIME_PINS: dict[str, dict[str, Any]] = {
    "plotly-host": {
        "version": "0.12.0-host",
        "path": "assets/plotly/host.js",
        "digest": _digest_file(_ASSETS / "plotly" / "host.js"),
        "maturity": "experimental",
    },
    "vega-host": {
        "version": "0.12.0-host",
        "path": "assets/vega/host.js",
        "digest": _digest_file(_ASSETS / "vega" / "host.js"),
        "maturity": "experimental",
    },
    "plotly": {
        "version": "2.35.0",
        "path": "assets/plotly/plotly.min.js",
        "digest": _digest_file(_ASSETS / "plotly" / "plotly.min.js"),
        "maturity": "experimental",
    },
    "vega": {
        "version": "5.30.0",
        "path": "assets/vega/vega.min.js",
        "digest": _digest_file(_ASSETS / "vega" / "vega.min.js"),
        "maturity": "experimental",
    },
    "vega-embed": {
        "version": "6.26.0",
        "path": "assets/vega/vega-embed.min.js",
        "digest": _digest_file(_ASSETS / "vega" / "vega-embed.min.js"),
        "maturity": "experimental",
    },
    "chartjs": {
        "version": "4.4.0",
        "path": "assets/chartjs/chart.umd.min.js",
        "digest": _digest_file(_ASSETS / "chartjs" / "chart.umd.min.js"),
        "maturity": "experimental",
    },
    "echarts": {
        "version": "5.5.0",
        "path": "assets/echarts/echarts.min.js",
        "digest": _digest_file(_ASSETS / "echarts" / "echarts.min.js"),
        "maturity": "experimental",
    },
    "mermaid": {
        "version": "10.9.0",
        "path": "assets/mermaid/mermaid.min.js",
        "digest": _digest_file(_ASSETS / "mermaid" / "mermaid.min.js"),
        "maturity": "experimental",
    },
    "maplibre": {
        "version": "4.5.0",
        "path": "assets/maplibre/maplibre-gl.js",
        "digest": _digest_file(_ASSETS / "maplibre" / "maplibre-gl.js"),
        "maturity": "experimental",
    },
}


def refresh_pin_digests() -> None:
    for name, meta in list(RUNTIME_PINS.items()):
        path = _ROOT / str(meta["path"])
        RUNTIME_PINS[name] = {**meta, "digest": _digest_file(path)}


def assert_pins_present() -> None:
    """Fail closed when offline pin bundles are missing or stubbed."""
    for name, meta in RUNTIME_PINS.items():
        path = _ROOT / str(meta["path"])
        if not path.is_file():
            raise error(
                "HED-CHART-0010",
                title="Chart runtime pin missing",
                explanation=f"Pinned runtime {name!r} is not packaged at {meta['path']}.",
                remediation="Reinstall hedron-charts or restore vendored offline assets.",
            )
        if _looks_like_stub(path):
            raise error(
                "HED-CHART-0010",
                title="Chart runtime pin is a stub",
                explanation=f"Pinned runtime {name!r} looks like a stub placeholder.",
                remediation="Vendor the real minified runtime matching RUNTIME_PINS versions.",
            )
        min_bytes = _MIN_BYTES.get(name)
        if min_bytes is not None and path.stat().st_size < min_bytes:
            raise error(
                "HED-CHART-0010",
                title="Chart runtime pin too small",
                explanation=(
                    f"Pinned runtime {name!r} is {path.stat().st_size} bytes; "
                    f"expected at least {min_bytes}."
                ),
                remediation="Vendor the real minified runtime matching RUNTIME_PINS versions.",
            )
    refresh_pin_digests()


# Back-compat alias used by older plugin drafts; now fail-closed.
def ensure_pin_stubs() -> None:
    assert_pins_present()


def pinned_runtime(name: str) -> dict[str, Any]:
    if name not in RUNTIME_PINS:
        raise KeyError(f"Unknown runtime pin {name!r}")
    return dict(RUNTIME_PINS[name])


def verify_pin(name: str, content: bytes) -> bool:
    meta = pinned_runtime(name)
    digest = "sha256:" + hashlib.sha256(content).hexdigest()
    expected = str(meta["digest"])
    return digest.endswith(expected.split(":")[-1]) or expected == content_digest(content)
