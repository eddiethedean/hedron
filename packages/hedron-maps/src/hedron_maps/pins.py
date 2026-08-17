"""Offline fingerprinted MapLibre pin (strict-CSP build, not charts 4.5.0)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from hedron_core.diagnostics import error
from hedron_core.identifiers import content_digest
from hedron_maps.limits import LIMITS

_ROOT = Path(__file__).resolve().parent
_ASSETS = _ROOT / "assets" / "maplibre"

MAPLIBRE_VERSION = "5.6.1"
_MIN_BYTES: dict[str, int] = {
    "maplibre-csp": 100_000,
    "maplibre-csp-worker": 50_000,
    "maplibre-css": 10_000,
}

__all__ = [
    "MAPLIBRE_VERSION",
    "RUNTIME_PINS",
    "assert_pins_present",
    "pinned_runtime",
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
    "maplibre-csp": {
        "version": MAPLIBRE_VERSION,
        "path": "assets/maplibre/maplibre-gl-csp.js",
        "digest": _digest_file(_ASSETS / "maplibre-gl-csp.js"),
        "maturity": "supported",
        "min_bytes": _MIN_BYTES["maplibre-csp"],
    },
    "maplibre-csp-worker": {
        "version": MAPLIBRE_VERSION,
        "path": "assets/maplibre/maplibre-gl-csp-worker.js",
        "digest": _digest_file(_ASSETS / "maplibre-gl-csp-worker.js"),
        "maturity": "supported",
        "min_bytes": _MIN_BYTES["maplibre-csp-worker"],
    },
    "maplibre-css": {
        "version": MAPLIBRE_VERSION,
        "path": "assets/maplibre/maplibre-gl.css",
        "digest": _digest_file(_ASSETS / "maplibre-gl.css"),
        "maturity": "supported",
        "min_bytes": _MIN_BYTES["maplibre-css"],
    },
}


def assert_pins_present() -> None:
    for name, meta in RUNTIME_PINS.items():
        path = _ROOT / str(meta["path"])
        if not path.is_file():
            raise error(
                "HED-MAP-RUNTIME-0002",
                title="Map runtime pin missing",
                explanation=f"Pinned runtime {name!r} is not packaged at {meta['path']}.",
                remediation="Reinstall hedron-maps or restore vendored MapLibre 5.6.1 assets.",
            )
        if _looks_like_stub(path):
            raise error(
                "HED-MAP-RUNTIME-0002",
                title="Map runtime pin is a stub",
                explanation=f"Pinned runtime {name!r} looks like a stub placeholder.",
                remediation="Vendor the real MapLibre 5.6.1 strict-CSP build.",
            )
        min_bytes = int(meta.get("min_bytes") or _MIN_BYTES.get(name, 0))
        if min_bytes and path.stat().st_size < min_bytes:
            raise error(
                "HED-MAP-RUNTIME-0002",
                title="Map runtime pin too small",
                explanation=(
                    f"Pinned runtime {name!r} is {path.stat().st_size} bytes; "
                    f"expected at least {min_bytes}."
                ),
                remediation="Vendor the real minified MapLibre 5.6.1 assets.",
            )
        RUNTIME_PINS[name] = {**meta, "digest": _digest_file(path)}


def pinned_runtime(name: str) -> dict[str, Any]:
    if name not in RUNTIME_PINS:
        raise KeyError(f"Unknown runtime pin {name!r}")
    return dict(RUNTIME_PINS[name])


def verify_pin(name: str, content: bytes) -> bool:
    meta = pinned_runtime(name)
    digest = "sha256:" + hashlib.sha256(content).hexdigest()
    expected = str(meta["digest"])
    return digest.endswith(expected.split(":")[-1]) or expected == content_digest(content)


def pin_facts() -> dict[str, Any]:
    return {
        "version": MAPLIBRE_VERSION,
        "charts_maplibre_pin": "4.5.0",
        "inherits_charts_pin": False,
        "strict_csp": True,
        "limits": dict(LIMITS),
    }
