"""HTMX extension asset contract (phase 0.7F). SSE is assigned to phase 0.10."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "ExtensionAsset",
    "SSE_EXTENSION_DEFERRED",
    "known_extensions",
]

SSE_EXTENSION_DEFERRED = True


@dataclass(frozen=True, slots=True)
class ExtensionAsset:
    name: str
    version: str
    digest: str
    path: str
    csp: str
    load_order: int
    deferred: bool = False
    notes: str = ""


def known_extensions() -> tuple[ExtensionAsset, ...]:
    return (
        ExtensionAsset(
            name="htmx-ext-sse",
            version="2.2.2",
            digest="sha256-deferred",
            path="/hedron-static/ext/sse.js",
            csp="script-src 'self'",
            load_order=50,
            deferred=True,
            notes="Official SSE extension evaluated; polling remains Supported (D-037).",
        ),
        ExtensionAsset(
            name="htmx-ext-head-support",
            version="2.0.2",
            digest="sha256-pending-pin",
            path="/hedron-static/ext/head-support.js",
            csp="script-src 'self'",
            load_order=10,
            deferred=True,
            notes="Optional; deferred until a first-party digest pin ships.",
        ),
    )
