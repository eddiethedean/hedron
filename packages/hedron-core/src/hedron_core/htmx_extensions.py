"""HTMX extension asset contract (phase 0.10: SSE and head-support pinned)."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "ExtensionAsset",
    "SSE_EXTENSION_DEFERRED",
    "known_extensions",
]

# Official SSE is Supported in 0.10; polling remains the required fallback (D-037/D-044).
SSE_EXTENSION_DEFERRED = False


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
            digest="sha256-83eca6fa0611fe2b0bf1700b424b88b5eced38ef448ef9760a2ea08fbc875611",
            path="/hedron-static/ext/sse.js",
            csp="script-src 'self'",
            load_order=50,
            deferred=False,
            notes="Official SSE extension; polling remains Supported fallback (D-044).",
        ),
        ExtensionAsset(
            name="htmx-ext-head-support",
            version="2.0.2",
            digest="sha256-207f449ba70ad0d384b1734288ddae8493d26737bd74d8510829c0be5b737568",
            path="/hedron-static/ext/head-support.js",
            csp="script-src 'self'",
            load_order=10,
            deferred=False,
            notes="Optional head merge for registered fragment assets (RFC-0032).",
        ),
    )
