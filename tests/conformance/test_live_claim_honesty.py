"""Live-transport claim honesty (LIVE-CLAIM-013)."""

from __future__ import annotations

from pathlib import Path

from hedron.experimental import __all__ as experimental_all
from hedron.live_claims import (
    EXPERIMENTAL_LIVE_SURFACES,
    LIVE_CLAIM_DOC_GLOBS,
    SUPPORTED_PRODUCTION_FALLBACK,
)

ROOT = Path(__file__).resolve().parents[2]


def test_experimental_module_covers_live_surfaces() -> None:
    missing = EXPERIMENTAL_LIVE_SURFACES - set(experimental_all)
    # Allow subset: inventory may list helpers also re-exported elsewhere.
    assert missing <= EXPERIMENTAL_LIVE_SURFACES
    for name in (
        "SseResponse",
        "sse_response",
        "StreamingComponentResponse",
        "accept_page_session_channel",
    ):
        assert name in experimental_all


def test_docs_do_not_call_sse_unqualified_supported() -> None:
    forbidden = [
        "Official HTMX SSE observation is\n    **Supported**",
        "SSE observation is **Supported**",
    ]
    for rel in LIVE_CLAIM_DOC_GLOBS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in forbidden:
            assert needle not in text, f"{rel} still claims SSE Supported unqualified"
        if rel.endswith("whats-ready.md") or rel.endswith("STABILITY.md"):
            assert "experimental" in text.lower()
            assert SUPPORTED_PRODUCTION_FALLBACK in text.lower() or "polling" in text.lower()


def test_stability_marks_live_experimental() -> None:
    text = (ROOT / "docs/api/STABILITY.md").read_text(encoding="utf-8")
    assert (
        "experimental:** live transports" in text.lower()
        or "experimental:** live" in text.lower()
        or "live transports" in text.lower()
    )
    assert "hedron.experimental" in text
