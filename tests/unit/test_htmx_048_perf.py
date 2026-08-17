"""PERF-048 measured asset bytes and zero unused cost after opt-out."""

from __future__ import annotations

from pathlib import Path

from tests.unit._helpers_048 import injected_page

from hedron_core.builtins import Text
from hedron_core.htmx_extensions import known_extensions

# Stage 1 measured uncompressed bytes (HTMX extension files as vendored).
PRELOAD_BYTES = 14099
SSE_BYTES = 8896
HEAD_SUPPORT_BYTES = 6285


def test_opt_out_has_zero_extension_bytes() -> None:
    html, _ = injected_page(Text("ok"), htmx_extensions=())
    assert "ext/sse.js" not in html
    assert "ext/head-support.js" not in html
    assert "ext/preload.js" not in html


def test_measured_asset_sizes() -> None:
    sizes = {}
    for ext in known_extensions():
        rel = ext.path.removeprefix("/hedron-static/")
        path = Path("packages/hedron-core/src/hedron_core/static") / rel
        sizes[ext.public_id] = path.stat().st_size
    assert sizes["preload"] == PRELOAD_BYTES
    assert sizes["sse"] == SSE_BYTES
    assert sizes["head-support"] == HEAD_SUPPORT_BYTES
    lock = Path("docs/acceptance/htmx-asset-activation-048.toml").read_text(encoding="utf-8")
    assert "preload_uncompressed_bytes" in lock
    assert str(PRELOAD_BYTES) in lock
