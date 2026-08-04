"""HTMX extension contract."""

from __future__ import annotations

from pathlib import Path

from hedron_core.htmx_extensions import SSE_EXTENSION_DEFERRED, known_extensions


def test_sse_pinned_and_assets_served() -> None:
    assert SSE_EXTENSION_DEFERRED is False
    exts = {e.name: e for e in known_extensions()}
    assert exts["htmx-ext-sse"].deferred is False
    assert exts["htmx-ext-head-support"].deferred is False
    assert exts["htmx-ext-sse"].digest.startswith("sha256-")
    assert exts["htmx-ext-head-support"].digest.startswith("sha256-")
    assert exts["htmx-ext-head-support"].path.startswith("/hedron-static/")
    assert exts["htmx-ext-sse"].path.startswith("/hedron-static/")

    static_root = (
        Path(__file__).resolve().parents[2]
        / "packages"
        / "hedron"
        / "src"
        / "hedron"
        / "static"
        / "ext"
    )
    assert (static_root / "sse.js").is_file()
    assert (static_root / "head-support.js").is_file()
