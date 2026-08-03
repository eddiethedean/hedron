"""HTMX extension contract."""

from __future__ import annotations

from hedron_core.htmx_extensions import SSE_EXTENSION_DEFERRED, known_extensions


def test_sse_deferred_and_assets_declared() -> None:
    assert SSE_EXTENSION_DEFERRED is True
    exts = {e.name: e for e in known_extensions()}
    assert exts["htmx-ext-sse"].deferred is True
    assert exts["htmx-ext-head-support"].path.startswith("/hedron-static/")
