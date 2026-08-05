"""Offline fingerprinted chart runtime pins."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from hedron_core.identifiers import content_digest

_ROOT = Path(__file__).resolve().parent
_ASSETS = _ROOT / "assets"

__all__ = ["RUNTIME_PINS", "ensure_pin_stubs", "pinned_runtime", "verify_pin"]


def _digest_file(path: Path) -> str:
    if not path.is_file():
        return "sha256:" + ("0" * 64)
    return content_digest(path.read_bytes())


RUNTIME_PINS: dict[str, dict[str, Any]] = {
    "plotly-host": {
        "version": "0.12.0-host",
        "path": "assets/plotly/host.js",
        "digest": _digest_file(_ASSETS / "plotly" / "host.js"),
    },
    "vega-host": {
        "version": "0.12.0-host",
        "path": "assets/vega/host.js",
        "digest": _digest_file(_ASSETS / "vega" / "host.js"),
    },
    "plotly": {
        "version": "2.35.0",
        "path": "assets/plotly/plotly.min.js",
        "digest": _digest_file(_ASSETS / "plotly" / "plotly.min.js"),
    },
    "vega": {
        "version": "5.30.0",
        "path": "assets/vega/vega.min.js",
        "digest": _digest_file(_ASSETS / "vega" / "vega.min.js"),
    },
    "vega-embed": {
        "version": "6.26.0",
        "path": "assets/vega/vega-embed.min.js",
        "digest": _digest_file(_ASSETS / "vega" / "vega-embed.min.js"),
    },
    "chartjs": {
        "version": "4.4.0",
        "path": "assets/chartjs/chart.umd.min.js",
        "digest": _digest_file(_ASSETS / "chartjs" / "chart.umd.min.js"),
    },
}


def ensure_pin_stubs() -> None:
    """Create fail-closed stub vendor files when full bundles are not vendored."""
    stubs = {
        _ASSETS
        / "plotly"
        / "plotly.min.js": "/* hedron plotly pin stub — supply offline bundle */\n",
        _ASSETS / "vega" / "vega.min.js": "/* hedron vega pin stub — supply offline bundle */\n",
        _ASSETS / "vega" / "vega-embed.min.js": "/* hedron vega-embed pin stub */\n",
        _ASSETS / "chartjs" / "chart.umd.min.js": "/* hedron chartjs pin stub */\n",
    }
    for path, body in stubs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.is_file():
            path.write_text(body, encoding="utf-8")
    # refresh digests after stubs
    for name, meta in RUNTIME_PINS.items():
        path = _ROOT / str(meta["path"])
        RUNTIME_PINS[name] = {
            **meta,
            "digest": _digest_file(path),
        }


def pinned_runtime(name: str) -> dict[str, Any]:
    if name not in RUNTIME_PINS:
        raise KeyError(f"Unknown runtime pin {name!r}")
    return dict(RUNTIME_PINS[name])


def verify_pin(name: str, content: bytes) -> bool:
    meta = pinned_runtime(name)
    digest = "sha256:" + hashlib.sha256(content).hexdigest()
    # content_digest may use a different prefix; compare hex suffix
    expected = str(meta["digest"])
    return digest.endswith(expected.split(":")[-1]) or expected == content_digest(content)
