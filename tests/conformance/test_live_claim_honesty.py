"""Live-transport claim honesty (LIVE-CLAIM-013)."""

from __future__ import annotations

from pathlib import Path

import hedron_django
import hedron_flask
from hedron.experimental import __all__ as experimental_all
from hedron.live_claims import (
    EXPERIMENTAL_LIVE_SURFACES,
    FORBIDDEN_LIVE_SUPPORTED_PHRASES,
    LIVE_CLAIM_DOC_GLOBS,
    SUPPORTED_PRODUCTION_FALLBACK,
)
from hedron_django.experimental import __all__ as django_experimental_all
from hedron_flask.experimental import __all__ as flask_experimental_all

ROOT = Path(__file__).resolve().parents[2]


def test_experimental_module_covers_live_surfaces() -> None:
    missing = EXPERIMENTAL_LIVE_SURFACES - set(experimental_all)
    assert not missing, f"experimental exports missing live surfaces: {sorted(missing)}"
    for name in (
        "SseResponse",
        "sse_response",
        "StreamingComponentResponse",
        "accept_page_session_channel",
    ):
        assert name in experimental_all


def test_adapter_roots_do_not_export_live_sse_stream() -> None:
    """Flask/Django package roots must not list experimental live helpers (0.24)."""
    for name in ("sse_response", "stream_text"):
        assert name not in hedron_flask.__all__
        assert name not in hedron_django.__all__
        assert name in flask_experimental_all
        assert name in django_experimental_all


def test_docs_do_not_call_sse_unqualified_supported() -> None:
    for rel in LIVE_CLAIM_DOC_GLOBS:
        path = ROOT / rel
        assert path.is_file(), f"missing live-claim doc: {rel}"
        text = path.read_text(encoding="utf-8")
        for needle in FORBIDDEN_LIVE_SUPPORTED_PHRASES:
            assert needle not in text, (
                f"{rel} still claims SSE/live Supported unqualified: {needle!r}"
            )
        if rel.endswith("whats-ready.md") or rel.endswith("STABILITY.md"):
            assert "experimental" in text.lower()
            assert SUPPORTED_PRODUCTION_FALLBACK in text.lower() or "polling" in text.lower()


def test_stability_marks_live_experimental() -> None:
    text = (ROOT / "docs/api/STABILITY.md").read_text(encoding="utf-8")
    lowered = text.lower()
    assert (
        "experimental:** live transports" in lowered
        or "experimental:** live" in lowered
        or ("live transports" in lowered and "experimental" in lowered)
    )
    assert "hedron.experimental" in text
